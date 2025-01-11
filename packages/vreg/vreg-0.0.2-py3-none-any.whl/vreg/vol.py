import numpy as np

from vreg import mod_affine, metrics, utils, optimize

class Volume3D:
    """
    A spatially aware numpy array
    
    Args:
        values (np.ndarray): 2D or 3D numpy array with values
        affine (np.ndarray): 4x4 numpy array with the affine matrix 
            of the value array. If not provided, the identity is assumed. 
            Defaults to None.    
    """

    def __init__(self, values:np.ndarray, affine:np.ndarray):

        if not isinstance(values, np.ndarray):
            raise ValueError('values must be a numpy array.')
        
        if not isinstance(affine, np.ndarray):
            raise ValueError('affine must be a numpy array.')
        
        if values.ndim not in [2,3]:
            raise ValueError('values must have 2 or 3 dimensions.')
        
        if affine.shape != (4,4):
            raise ValueError('affine must be a 4x4 array.')
        
        # TODO: Not good because you can't be sure axis 2 is right
        # This must be handled in volume() and Volume3D should always receive 
        # a 3D array of values
        if values.ndim == 2: 
            values = np.expand_dims(values, axis=2)
        
        self._values = values
        self._affine = affine
    
    @property
    def values(self):
        return self._values
    
    @property
    def affine(self):
        return self._affine
    
    @property
    def shape(self):
        return self._values.shape
    
    @property
    def spacing(self):
        return np.linalg.norm(self.affine[:3,:3], axis=0)
    
    def copy(self, **kwargs):
        """Return a copy

        Args:
            kwargs: Any keyword arguments accepted by `numpy.copy`.

        Returns:
            Volume3D: copy
        """
        return Volume3D(
            self.values.copy(**kwargs), 
            self.affine.copy(**kwargs),
        )
    
    def extract_slice(self, z=0):
        """Extract a slice at index z

        Args:
            z (int, optional): slice index

        Returns:
            vreg.Volume3D: one-slice Volume3D at index z
        """
        values, affine = utils.extract_slice(self.values, self.affine, z)
        return Volume3D(values.copy(), affine.copy())


    def split(self, n=None, axis=-1, gap=0):
        """Split a volume into slices (2D volumes)

        Args:
            n (int, optional): number of slices in the result. If this is not 
              provided, n is the shape of the volume in the axis along which 
              it is split. Defaults to None.
            axis (int, optional): Axis along which to split the volume. 
              Defaults to -1 (z-axis).
            gap (float, optional): Add a gap (in mm) between the resulting 
              slices. Defaults to 0.

        Returns:
            list of Volume3D: a list of volumes with a single slice each.
        """
        # If the number of slices required is different from the current 
        # number of slices, then first resample the volume.
        if n == self.shape[axis]:
            vol = self
        else:
            spacing = self.spacing
            spacing[axis] = spacing[axis]*self.shape[axis]/n
            vol = self.resample(spacing) 

        # Split up the volume into a list of 2D volumes.
        mat = vol.affine[:3,:3]
        split_vec = mat[:, axis] 
        split_unit_vec = split_vec/self.spacing[axis]
        vols = []
        for i in range(vol.shape[axis]):
            
            # Shift the affine by i positions along the slice axis.
            affine_i = vol.affine.copy()
            affine_i[:3, 3] += i*split_vec + i*gap*split_unit_vec

            # Take the i-th slice and add a dimension of 1 to make a 3D array.
            values_i = vol.values.take(i, axis=axis)
            values_i = np.expand_dims(values_i, axis=axis)

            # Build the volume and add to the list.
            vol_i = Volume3D(values_i, affine_i)
            vols.append(vol_i)
        return vols

    
    def add(self, v, *args, **kwargs):
        """Add another volume

        Args:
            v (Volume3D): volume to add. If this is in a different geometry, it 
                will be resliced first
            args, kwargs: arguments and keyword arguments of `numpy.add`.

        Returns:
            Volume3D: sum of the two volumes
        """
        v = v.slice_like(self)
        values = np.add(self.values, v.values, *args, **kwargs)
        return Volume3D(values, self.affine)
    
    def subtract(self, v, *args, **kwargs):
        """Subtract another volume

        Args:
            v (Volume3D): volume to subtract. If this is in a different 
                geometry, it will be resliced first
            args, kwargs: arguments and keyword arguments of `numpy.subtract`.

        Returns:
            Volume3D: sum of the two volumes
        """
        v = v.slice_like(self)
        values = np.subtract(self.values, v.values, *args, **kwargs)
        return Volume3D(values, self.affine)
    
    def bounding_box(self, mask=None, margin=0.0):
        """Return the bounding box

        Args:
            mask (Volume3D, optional): If mask is None, the bounding box is 
                drawn around the non-zero values of the Volume3D. If mask is 
                provided, it is drawn around the non-zero values of mask 
                instead. Defaults to None.
            margin (float, optional): How big a margin (in mm) around the 
                object. Defaults to 0.

        Returns:
            Volume3D: the bounding box
        """
        if mask is None:
            values, affine = mod_affine.mask_volume(
                self.values, self.affine, self.values, self.affine, margin)
        else:
            values, affine = mod_affine.mask_volume(
                self.values, self.affine, mask.values, mask.affine, margin)
        return Volume3D(values, affine)


    def resample(self, spacing=None, stretch=None):
        """Resample volume to new pixel spacing

        Args:
            spacing (array-like, optional): New pixel spacing in mm. Generally 
                this is a 3-element array but for isotropic resampling this can 
                be a scalar value. If this is not provided, the volume is 
                resampled according to the specified stretch. Defaults to None.
            stretch (float, optional): Rescale pixel size with this value. 
                Generally this is a 3-element array, one for each dimension. If 
                a scalar value is provided, all dimensions are resampled with 
                the same stretch factor. This argument is ignored if a spacing is 
                provided explicitly. Defaults to None (no resampling).

        Raises:
            ValueError: if spacing or stretch have the wrong size.

        Returns:
            vreg.Volume3D: resampled volume
        """
        # Set defaults
        if stretch is None:
            stretch = 1.0

        # Affine components
        rot, trans, ps = utils.affine_components(self.affine)

        # Get new pixel spacing
        if spacing is None:
            if np.isscalar(stretch):
                spacing = ps*stretch
            elif np.size(stretch)==3:
                spacing = ps*stretch
            else:
                raise ValueError(
                    'stretch must be a scalar or a 3-element array')
        elif np.isscalar(spacing):
            spacing = np.full(3, spacing)
        elif np.size(spacing) != 3:
            raise ValueError(
                'spacing must be a scalar or a 3-element array')
        
        # Resample
        affine = utils.affine_matrix(rotation=rot, translation=trans, 
                                     pixel_spacing=spacing)
        values, _ = mod_affine.affine_reslice(self.values, self.affine, affine)

        # Return volume
        return Volume3D(values, affine)
    

    def find_transform_to(
            self, target, transform, params=None, metric=None, 
            optimizer=None, resolutions=None, 
            mask=None, target_mask=None, **kwargs):
        """Coregister a volume to a static target volume.

        Args:
            target (vreg.Volume3D): Fixed target volume for the coregistration.
            transform (str, optional): Coordinate transformation. 
              Possible values are 'translate', 'rotate', 'stretch', 
              'transform_rigid', 'transform_affine'.
            params (array-like, optional): Initial parameters of the 
              transformation. Defaults to None.
            metric (func, optional): Metric to quantify goodness of alignment. 
              Options are 'mi' (mutual information), 'sos' (sum of squares), 
              and 'migrad' (mutual information of the image gradient).  
              Default is 'mi'.
            optimizer (dict, optional): Optimizer as a dictionary 
              with one key *method* specifying the method used for optimization. 
              The other items in the dictionary are any optional keywords 
              accepted by the method. Defaults to {'method':'LS'}.
            resolutions (list, optional): Resolutions to use in the 
              optimization. Defaults to [1].
            mask (Volume3D, optional): volume used for masking the moving 
              volume. Defaults to None.
            target_mask (Volume3D, optional): volume used for masking the 
              static volume. Defaults to None.
            kwargs (dict, optional): optional keyword arguments for the 
              transform function.

        Returns:
            params: The optimal values for the transformaton parameters.
        """
        # Defaults
        if metric is None:
            metric = 'mi'
        if optimizer is None:
            optimizer = {'method':'LS'}
        if resolutions is None:
            resolutions = [1]

        # Perform multi-resolution loop
        mask_resampled = None
        target_ind = None

        for res in resolutions:

            if res == 1:
                moving = self
                target_resampled = target
            else:
                # Downsample
                moving = self.resample(stretch=res)
                target_resampled = target.resample(stretch=res)

            # resample the masks
            if mask is not None:
                mask_resampled = mask.slice_like(moving)
            if target_mask is not None:
                target_mask_resampled = target_mask.slice_like(target_resampled)
                target_ind = np.where(target_mask_resampled.values >= 0.5)

            args = (
                target_resampled, transform, metric, mask_resampled, 
                target_ind, kwargs,
            )
            params = optimize.minimize(
                moving._dist, params, args=args, **optimizer)
            
        return params

    def _dist(self, params, target, transform, metric, mask, target_ind, 
              kwargs):
        return self.distance(target, transform, params, metric, mask, 
                                   target_ind, **kwargs)

    def distance(self, target, transform, params, metric='mi', mask=None, 
                       target_ind=None, **kwargs):
        """Distance to a target volume after a transform

        Args:
            target (vreg.Volume3D): Target volume
            transform (str, optional): Coordinate transformation. 
              Possible values are 'translate', 'rotate', 'stretch', 
              'transform_rigid', 'transform_affine'.
            params (array-like, optional): Initial parameters of the 
              transformation. Defaults to None.
            metric (func, optional): Metric to quantify distance. 
              Options are 'mi' (mutual information), 'sos' (sum of squares), 
              and 'migrad' (mutual information of the image gradient).  
              Default is 'mi'.
            mask (Volume3D, optional): volume used for masking the moving 
              volume. Defaults to None.
            target_ind (numpy.ndarray, optional): Indices in the target 
              volume that count towards the distance. Defaults to None.

        Returns:
            float: distance after transform
        """
        if metric == 'mi':
            metric = metrics.mutual_information
        elif metric == 'sos':
            metric = metrics.sum_of_squares
        elif metric == 'migrad':
            metric = metrics.mi_grad

        # Transform the moving image to the target
        moving = self.transform_to(target, transform, params, **kwargs)
        
        # Transform the moving mask
        mask_ind = None
        if mask is not None:
            mask = mask.transform_to(target, transform, params, **kwargs)
            mask_ind = np.where(mask >= 0.5)

        # Calculate metric in indices exposed by the mask(s)
        if target_ind is None and mask_ind is None:
            return metric(target.values, moving.values)
        
        if target_ind is None and mask_ind is not None:
            ind = mask_ind
        elif target_ind is not None and mask_ind is None:
            ind = target_ind
        elif target_ind is not None and mask_ind is not None:
            ind = target_ind or mask_ind
        return metric(target.values[ind], moving.values[ind])
    
        
    def transform_to(self, target, transform, params, **kwargs):
        """Transform a volume to a target volume

        Args:
            target (vreg.Volume3D): Target volume
            transform (str, optional): Coordinate transformation. 
              Possible values are 'translate', 'rotate', 'stretch', 
              'transform_rigid', 'transform_affine'.
            params (array-like, optional): Initial parameters of the 
              transformation. Defaults to None.

        Returns:
            vreg.Volume3D: transformed volume
        """
        return getattr(self, transform + '_to')(target, params, **kwargs)
    
    def transform(self, transform, params, **kwargs):
        """Transform a volume

        Args:
            transform (str, optional): Coordinate transformation. 
              Possible values are 'translate', 'rotate', 'stretch', 
              'transform_rigid', 'transform_affine'.
            params (array-like, optional): Initial parameters of the 
              transformation. Defaults to None.

        Returns:
            vreg.Volume3D: transformed volume
        """
        return getattr(self, transform)(params, **kwargs)


    def find_transform_rigid_to(
            self, target, params=None, metric=None, 
            optimizer=None, resolutions=None, 
            mask=None, target_mask=None, center=None, coords='fixed'):
        """Find the rigid transform to a static target volume.

        Args:
            target (vreg.Volume3D): Fixed target volume for the coregistration.
            params (array-like): 6-element vector with translation and  
              rotation vectors, in that order. 
            metric (func, optional): Metric to quantify goodness of alignment. 
              Options are 'mi' (mutual information), 'sos' (sum of squares), 
              and 'migrad' (mutual information of the image gradient).  
              Default is 'mi'.
            optimizer (dict, optional): Optimizer as a dictionary 
              with one key *method* specifying the method used for optimization. 
              The other items in the dictionary are any optional keywords 
              accepted by the method. Defaults to {'method':'LS'}.
            resolutions (list, optional): Resolutions to use in the 
              optimization. Defaults to [1].
            mask (Volume3D, optional): volume used for masking the moving 
              volume. Defaults to None.
            target_mask (Volume3D, optional): volume used for masking the 
              static volume. Defaults to None.
            center (str or array-like): center of rotation. If this has value 
              'com', the rotation is performed around the center of mass. 
              Alternatively this can be a 3-element vector. Defaults to None 
              (center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            params: The optimal values for the transformaton parameters.
        """
        return self.find_transform_to(
            target, 'transform_rigid', params=params, metric=metric, 
            optimizer=optimizer, resolutions=resolutions, 
            mask=mask, target_mask=target_mask, center=center, coords=coords)

    def find_rotate_to(
            self, target, rotation=None, metric=None, 
            optimizer=None, resolutions=None, 
            mask=None, target_mask=None, center=None, coords='fixed'):
        """Find the rigid transform to a static target volume.

        Args:
            target (vreg.Volume3D): Fixed target volume for the coregistration.
            rotation (array-like): 3-element rotation vector. 
            metric (func, optional): Metric to quantify goodness of alignment. 
              Options are 'mi' (mutual information), 'sos' (sum of squares), 
              and 'migrad' (mutual information of the image gradient).  
              Default is 'mi'.
            optimizer (dict, optional): Optimizer as a dictionary 
              with one key *method* specifying the method used for optimization. 
              The other items in the dictionary are any optional keywords 
              accepted by the method. Defaults to {'method':'LS'}.
            resolutions (list, optional): Resolutions to use in the 
              optimization. Defaults to [1].
            mask (Volume3D, optional): volume used for masking the moving 
              volume. Defaults to None.
            target_mask (Volume3D, optional): volume used for masking the 
              static volume. Defaults to None.
            center (str or array-like): center of rotation. If this has value 
              'com', the rotation is performed around the center of mass. 
              Alternatively this can be a 3-element vector. Defaults to None 
              (center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            params: The optimal values for the transformaton parameters.
        """
        return self.find_transform_to(
            target, 'rotate', params=rotation, metric=metric, 
            optimizer=optimizer, resolutions=resolutions, 
            mask=mask, target_mask=target_mask, center=center, coords=coords)
    
    
    def find_translate_to(
            self, target, translation=None, metric=None, 
            optimizer=None, resolutions=None, 
            mask=None, target_mask=None, coords='fixed'):
        """Find the translation to a static target volume.

        Args:
            target (vreg.Volume3D): Fixed target volume for the coregistration.
            translation (array-like, optional): Initial values for the 
              translation vector. Defaults to None.
            metric (func, optional): Metric to quantify goodness of alignment. 
              Options are 'mi' (mutual information), 'sos' (sum of squares), 
              and 'migrad' (mutual information of the image gradient).  
              Default is 'mi'.
            optimizer (dict, optional): Optimizer as a dictionary 
              with one key *method* specifying the method used for optimization. 
              The other items in the dictionary are any optional keywords 
              accepted by the method. Defaults to {'method':'LS'}.
            resolutions (list, optional): Resolutions to use in the 
              optimization. Defaults to [1].
            mask (Volume3D, optional): volume used for masking the moving 
              volume. Defaults to None.
            target_mask (Volume3D, optional): volume used for masking the 
              static volume. Defaults to None.
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation vector, as a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            params: The optimal values for the transformaton parameters.
        """
        return self.find_transform_to(
            target, 'translate', params=translation, metric=metric, 
            optimizer=optimizer, resolutions=resolutions, 
            mask=mask, target_mask=target_mask, coords=coords)


    def _affine_matrix(self, translation, rotation, center, stretch, coords):
        # Helper function

        # Initialize
        if translation is None:
            translation = np.zeros(3)
        if rotation is None:
            rotation = np.zeros(3)
        if stretch is None:
            stretch = np.ones(3)
        if center is None:
            center = np.zeros(3)

        # Check inputs
        if 0 != np.count_nonzero(stretch <= 0):
            raise ValueError(
                "All elements of stretch must be strictly positive")
        if isinstance(coords, str):
            if coords not in ['fixed','volume']:
                raise ValueError(
                    coords + " is not a valid reference frame. The options "
                    "are 'volume' and 'fixed'.")
        elif np.shape(coords) != (4,4):
            raise ValueError(
                "coords must either be a string or an affine array")
        if isinstance(center, str):
            if center not in ['com']:
                raise ValueError(
                    "center must be a vector or the string 'com'.")
        elif np.size(center) != 3:
            raise ValueError(
                "center must either be a string or a 3-element vector.")

        # Convert to fixed reference frame
        if isinstance(coords, str):
            if coords=='fixed':
                if isinstance(center, str):
                    center = self.center_of_mass(coords='fixed')
            elif coords=='volume':
                translation = utils.volume_vector(translation, self.affine)
                rotation = utils.volume_vector(rotation, self.affine)
                if isinstance(center, str):
                    center = self.center_of_mass(coords='fixed')
                else:
                    center = utils.vol2fix(center, self.affine)
        else:
            translation = utils.volume_vector(translation, coords)
            rotation = utils.volume_vector(rotation, coords)
            if isinstance(center, str):
                center = self.center_of_mass(coords='fixed')
            else:
                center = utils.vol2fix(center, coords)
                
        # Get affine transformation
        return utils.affine_matrix(rotation, translation, stretch, center)


    def center_of_mass(self, coords='fixed'):
        """
        Center of mass.

        Args:
            coords (str or array, optional): Reference frame for the 
              coordinates of the returned vector, as a 4x4 affine array. 
              String options are shorthand notations: 'fixed' (patient 
              reference), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            numpy.ndarray: 3-element vector pointing to the volume's center of 
            mass.
        """ 
        return utils.center_of_mass(self.values, self.affine, coords=coords)


    def reslice(self, affine=None, orient=None, rotation=None, center=None, 
                spacing=1.0, coords='fixed'):
        """Reslice the volume.

        Args:
            affine (array, optional): 4x4 affine array providing the affine 
              of the result. If this is not provided, the affine array is 
              constructed from the other arguments. Defaults to None.
            orient (str, optional): Orientation of the volume. The options are 
              'axial', 'sagittal', or 'coronal'. Alternatively the same options 
              can be provided referring to the orientation of the image planes: 
              'xy' (axial), 'yz' (sagittal) or 'zx' (coronal). If None is 
              provided, the current orientation of the volume is used. 
              Defaults to None.
            rotation (array, optional): 3-element array specifying the rotation 
              relative to *orient*, or relative to the current orientation 
              of the volume (if *orient* is None). Defaults to None.
            center (array, optional): 3-element array specifying the rotation 
              center of the new reference frame, in case a rotation is provided. 
              Defaults to None.
            spacing (float, optional): Pixel spacing in mm. Can be a 3D array or 
              a single scalar for isotropic spacing. Defaults to 1.0.
            coords (str or array, optional): Reference frame for the 
              coordinates of the rotation and center vector, as a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            Volume3D: resliced volume
        """

        if affine is None:
            
            # Convert to fixed coordinates
            if isinstance(coords, str):
                if coords=='volume':
                    if rotation is not None:
                        rotation = utils.volume_vector(rotation, self.affine)
                    if center is not None:
                        center = utils.vol2fix(center, self.affine)
            else:
                if rotation is not None:
                    rotation = utils.volume_vector(rotation, coords)
                if center is not None:
                    center = utils.vol2fix(center, coords)                

            # Determine affine
            if orient is None:
                transfo = utils.affine_matrix(
                    rotation=rotation, center=center, pixel_spacing=spacing)
                affine = transfo.dot(self.affine)
            else:
                affine = utils.make_affine(orient, rotation, center, spacing) 

        # Perform an active transform with the inverse
        transfo_inv = self.affine.dot(np.linalg.inv(affine))
        values, affine = mod_affine.affine_transform(
            self.values, self.affine, transfo_inv, reshape=True)
        
        # Transform the affine with the forward
        transfo = np.linalg.inv(transfo_inv)
        affine = transfo.dot(affine)

        return Volume3D(values, affine)

    
    def slice_like(self, v):
        """Slice the volume to the geometry of another volume

        Args:
            v (Volume3D): reference volume with desired orientation and shape.

        Returns:
            Volume3D: resliced volume
        """
        values, affine = mod_affine.affine_reslice(
            self.values, self.affine, 
            v.affine, output_shape=v.shape)
        return Volume3D(values, affine)

    
    def transform_affine_to(self, target, params, center=None, coords='fixed'):
        """Apply an affine transformation and reslice the result to the 
        geometry of a target volume.

        Args:
            target (vreg.Volume3D): target volume
            params (array-like): 9-element vector with translation vector,  
              rotation vector and stretch factors, in that order. 
            center (str or array-like, optional): center of rotation. If this 
              has value 'com' the rotation is performed 
              around the center of mass. Alternatively this can be a 
              3-element vector. Defaults to None (center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        translation = params[:3]
        rotation = params[3:6]
        stretch = params[6:9]

        # Get affine transformation
        transform = self._affine_matrix(translation, rotation, center, 
                                        stretch, coords)

        # Apply affine transformation
        values = mod_affine.affine_transform_and_reslice(
            self.values, self.affine, target.shape, target.affine, transform,
        )
        affine = target.affine.copy()
    
        # Return volume
        return Volume3D(values, affine)
    

    def transform_rigid_to(self, target, params, center=None, coords='fixed'):
        """Apply a rigid transformation and reslice the result to the 
        geometry of a target volume.

        Args:
            target (vreg.Volume3D): target volume
            params (array-like): 6-element vector with translation and 
              rotation vectors, in that order. 
            center (str or array-like): center of rotation. If this has value 
              'com' the rotation is performed around the 
              center of mass. Alternatively this can be a 3-element vector. 
              Defaults to None (center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        stretch = np.ones(3)
        params = np.concatenate((params, stretch))
        return self.transform_affine_to(target, params, coords=coords, 
                                        center=center)
    

    def rotate_to(self, target, rotation, center=None, coords='fixed'):
        """Apply a rotation and reslice the result to the 
        geometry of a target volume.

        Args:
            target (vreg.Volume3D): target volume
            rotation (array-like): 3-element rotation vector in radians. 
              Defaults to None (no rotation).
            center (str or array-like): center of rotation. If this has value 
              'com' the rotation is performed around the 
              center of mass. Alternatively this can be a 3-element vector. 
              Defaults to None (center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the rotation and center vector, as a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        translation = np.zeros(3)
        stretch = np.ones(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine_to(target, params, center=center, 
                                        coords=coords)


    def translate_to(self, target, translation, coords='fixed', dir='xyz'):
        """Apply a translation and reslice the result to the 
        geometry of a target volume.

        Args:
            target (vreg.Volume3D): target volume
            translation (array-like): translation vector (mm) with 1, 2 or 3 
              elements depending on the value of *dir*. 
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation vector, as a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.
            dir (str, optional): Allowed directions of the translation. The 
              options are 'xyz' (3D translation), 'xy' (2D in-slice 
              translation) and 'z' (through-slice translation). Defaults to 
              'xyz'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if dir=='xy':
            translation = np.concatenate((translation, [0]))
        elif dir=='z':
            translation = np.concatenate(([0,0], translation))
        rotation = np.zeros(3)
        stretch = np.ones(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine_to(target, params, coords=coords)
    

    def stretch_to(self, target, stretch):
        """Stretch and reslice to the geometry of a 
        target volume.

        Args:
            target (vreg.Volume3D): target volume
            stretch (array-like): 3-element stretch vector with strictly 
              positive dimensionless values (1 = no stretch).

        Returns:
            vreg.Volume3D: transformed volume.
        """
        translation = np.zeros(3)
        rotation = np.zeros(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine_to(target, params)
    

    def transform_affine(self, params, center=None, values=False, 
                         reshape=False, coords='fixed'):
        """Apply an affine transformation.

        Args:
            params (array-like): 9-element vector with translation vector,  
              rotation vector and stretch factors, in that order.
            center (str or array-like): center of rotation. If this has value 
              'com', the rotation is performed around the center of mass. 
              Alternatively this can be a 3-element vector. Defaults to None (
              center = origin).
            values (bool, optional): If set to True, the values are 
              transformed. Otherwise the affine is transformed. Defaults to 
              False.
            reshape (bool, optional): When values=True, reshape=False will 
              retain the shape and location of the volume. With reshape=True, 
              the volume will be reshaped to fit the transformed values. This 
              keyword is ignored when values=False. Defaults to False.
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        translation = params[:3]
        rotation = params[3:6]
        stretch = params[6:9]

        # Get affine transformation
        transform = self._affine_matrix(translation, rotation, center, 
                                        stretch, coords)

        # Apply affine transformation
        if values:
            values, affine = mod_affine.affine_transform(
                self.values, self.affine, transform, reshape)
        else:
            values = self.values.copy()
            affine = transform.dot(self.affine)
        return Volume3D(values, affine)
            

    def transform_rigid(self, params, values=False, reshape=False, 
                        center=None, coords='fixed'):
        """Apply a rigid transformation.

        Args:
            params (array-like): 6-element vector with translation and  
              rotation vectors, in that order. 
            values (bool, optional): If set to True, the values are 
              transformed. Otherwise the affine is transformed. Defaults to 
              False.
            reshape (bool, optional): When values=True, reshape=False will 
              retain the shape and location of the volume. With reshape=True, 
              the volume will be reshaped to fit the transformed values. This 
              keyword is ignored when values=False. Defaults to False.
            center (str or array-like): center of rotation. If this has value 
              'com', the rotation is performed around the center of mass. 
              Alternatively this can be a 3-element vector. Defaults to None (
              center = origin).
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation, rotation and center vector, as 
              a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        stretch = np.ones(3)
        params = np.concatenate((params, stretch))
        return self.transform_affine(params, center=center, values=values, 
                                     reshape=reshape, coords=coords)
        

    def rotate(self, rotation, center=None, values=False, reshape=False, 
               coords='fixed'):
        """Rotate the volume.

        Args:
            rotation (array-like): 3-element rotation vector in radians. 
            center (str or array-like): center of rotation. If this has value 
              'com', the rotation is performed around the center of mass. 
              Alternatively this can be a 3-element vector. Defaults to None (
              center = origin).
            values (bool, optional): If set to True, the values are 
              transformed. Otherwise the affine is transformed. Defaults to 
              False.
            reshape (bool, optional): When values=True, reshape=False will 
              retain the shape and location of the volume. With reshape=True, 
              the volume will be reshaped to fit the transformed values. This 
              keyword is ignored when values=False. Defaults to False.
            coords (str or array, optional): Reference frame for the 
              coordinates of the rotation and center vector, as a 4x4 affine 
              array. String options are shorthand notations: 'fixed' (patient 
              reference frame), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        translation = np.zeros(3)
        stretch = np.ones(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine(params, values=values, reshape=reshape, 
                                     center=center, coords=coords)


    def translate(self, translation, values=False, reshape=False, 
                  coords='fixed', dir='xyz'):
        """Translate the volume.

        Args:
            translation (array-like): translation vector (mm) with 1, 2 or 3 
              elements depending on the value of *dir*. 
            values (bool, optional): If set to True, the values are 
              transformed. Otherwise the affine is transformed. Defaults to 
              False.
            reshape (bool, optional): When values=True, reshape=False will 
              retain the shape and location of the volume. With reshape=True, 
              the volume will be reshaped to fit the transformed values. This 
              keyword is ignored when values=False. Defaults to False.
            coords (str or array, optional): Reference frame for the 
              coordinates of the translation vector, as a 4x4 affine array. 
              String options are shorthand notations: 'fixed' (patient 
              reference), and 'volume' (volume reference frame). Defaults 
              to 'fixed'.
            dir (str, optional): Allowed directions of the translation. The 
              options are 'xyz' (3D translation), 'xy' (2D in-slice 
              translation) and 'z' (through-slice translation). Defaults to 
              'xyz'.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        if dir=='xy':
            translation = np.concatenate((translation, [0]))
        elif dir=='z':
            translation = np.concatenate(([0,0], translation))
        rotation = np.zeros(3)
        stretch = np.ones(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine(params, values=values, reshape=reshape, 
                                     coords=coords)


    def stretch(self, stretch, values=False, reshape=False):
        """Stretch the volume.

        Args:
            stretch (array-like): 3-element stretch vector with strictly 
              positive dimensionless values (1 = no stretch). 
            values (bool, optional): If set to True, the values are 
              transformed. Otherwise the affine is transformed. Defaults to 
              False.
            reshape (bool, optional): When values=True, reshape=False will 
              retain the shape and location of the volume. With reshape=True, 
              the volume will be reshaped to fit the transformed values. This 
              keyword is ignored when values=False. Defaults to False.

        Returns:
            vreg.Volume3D: transformed volume.
        """
        translation = np.zeros(3)
        rotation = np.zeros(3)
        params = np.concatenate((translation, rotation, stretch))
        return self.transform_affine(params, values=values, reshape=reshape)



        
def volume(values, affine=None, orient='axial', rotation=None, center=None, 
           spacing=1.0, pos=[0,0,0]):
    """Create a new volume from an array of values

    Args:
        values (array): 2D or 3D array of values.
        affine (array, optional): 4x4 affine array. If this is not provided, 
          the affine array is constructed from the other arguments. Defaults 
          to None.
        orient (str, optional): Orientation of the volume. The options are 
          'axial', 'sagittal', or 'coronal'. Alternatively the same options 
          can be provided referring to the orientation of the image planes: 
          'xy' (axial), 'yz' (sagittal) or 'zx' (coronal). Defaults to 'axial.
        rotation (array, optional): 3-element array specifying a rotation 
          relative to *orient*. Defaults to None.
        center (array, optional): 3-element array specifying the rotation 
          center, in case a rotation is provided. Defaults to None.
        spacing (float, optional): Pixel spacing in mm. Can be a 3D array or 
          a single scalar for isotropic spacing. Defaults to 1.0.
        pos (list, optional): Position of the upper left-hand corner in mm. 
          Defaults to [0,0,0].

    Returns:
        vreg.Volume3D: volume with required orientation and position.
    """

    if affine is None:
        affine = utils.make_affine(orient, rotation, center, spacing, pos) 
    return Volume3D(values, affine)



def zeros(shape, affine=None, orient='axial', spacing=1.0, pos=[0,0,0], 
          **kwargs):
    """Return a new volume of given shape and affine, filled with zeros.

    Args:
        shape (int or tuple of ints): Shape of the new array, e.g., (2, 3) or 2.
        affine (array, optional): 4x4 affine array. If this is not provided, 
          the affine array is constructed from the other arguments. Defaults 
          to None.
        orient (str, optional): Orientation of the volume. The options are 
          'axial', 'sagittal', or 'coronal'. Alternatively the same options 
          can be provided referring to the orientation of the image planes: 
          'xy' (axial), 'yz' (sagittal) or 'zx' (coronal). Defaults to 'axial'.
        spacing (float, optional): Pixel spacing in mm. Can be a 3D array or 
          a single scalar for isotropic spacing. Defaults to 1.0.
        pos (list, optional): Position of the upper left-hand corner in mm. 
          Defaults to [0,0,0].
        kwargs: Any keyword arguments accepted by `numpy.zeros`.

    Returns:
        Volume3D: vreg.Volume3D with zero values.
    """
    values = np.zeros(shape, **kwargs)
    return volume(values, affine, orient, spacing, pos)


def full(shape, fill_value, affine=None, orient='axial', spacing=1.0, 
         pos=[0,0,0], **kwargs):
    """Return a new volume of given shape and affine, filled with *fill_value*.

    Args:
        shape (int or tuple of ints): Shape of the new array, e.g., (2, 3) or 2.
        fill_value (float): value to fill the array.
        affine (array, optional): 4x4 affine array. If this is not provided, 
          the affine array is constructed from the other arguments. Defaults 
          to None.
        orient (str, optional): Orientation of the volume. The options are 
          'axial', 'sagittal', or 'coronal'. Alternatively the same options 
          can be provided referring to the orientation of the image planes: 
          'xy' (axial), 'yz' (sagittal) or 'zx' (coronal). Defaults to 'axial'.
        spacing (float, optional): Pixel spacing in mm. Can be a 3D array or 
          a single scalar for isotropic spacing. Defaults to 1.0.
        pos (list, optional): Position of the upper left-hand corner in mm. 
          Defaults to [0,0,0].
        kwargs: Any keyword arguments accepted by `numpy.full`.

    Returns:
        Volume3D: vreg.Volume3D with *fill_value* values.
    """
    values = np.full(shape, fill_value, **kwargs)
    return volume(values, affine, orient, spacing, pos)


def zeros_like(v:Volume3D):
    """Return a new volume with same shape and affine as v, filled with zeros.

    Args:
        v (int or tuple of ints): Shape of the new array, e.g., (2, 3) or 2.

    Returns:
        Volume3D: vreg.Volume3D with zero values.
    """
    values = np.zeros(v.shape, dtype=v.values.dtype)
    return volume(values, v.affine.copy())


def full_like(v:Volume3D, fill_value):
    """Return a new volume with same shape and affine as v, filled with 
    *fill_value*.

    Args:
        v (int or tuple of ints): Shape of the new array, e.g., (2, 3) or 2.
        fill_value (float): value to fill the array.

    Returns:
        Volume3D: vreg.Volume3D with *fill_value* values.
    """
    values = np.full_like(v.values, fill_value)
    return volume(values, v.affine.copy())


def concatenate(vols, axis=2, prec=None, move=False):
    """Join a sequence of volumes along x-, y-, or z-axis.

    Volumes can only be joined up if they have the same shape 
    (except along the axis of concatenation), the same orientation and 
    the same voxel size.

    Args:
        vols (sequence of volumes): Volumes to concatenate.
        axis (int, optional): The axis along which the volumes will be 
          concatenated (x, y or z). Defaults to 2 (z-axis).
        prec (int, optional): precision to consider when comparing positions 
          and orientations of volumes. All differences are rounded off to this 
          digit before comparing them to zero. If this is not specified, 
          floating-point precision is used. Defaults to None.
        move (bool, optional): If this is set to True, the volumes are allowed 
          to move to the correct positions for concatenation. In this case 
          the first volume in the sequence will be fixed, and all others will 
          move to align with it. If move=False, volumes can only be 
          concatenated if they are already aligned in the direction of 
          concatenation without gaps between them, and in the correct order. 
          Defaults to False.

    Returns:
        Volume3D: The concatenated volume.
    """

    # Check arguments
    if not np.iterable(vols):
        raise ValueError(
            "vreg.stack() requires an iterable as argument.")
    if axis not in [0,1,2,-1,-2,-3]:
        raise ValueError(
            "Invalid axis argument. Volumes only have 3 axes.")

    # Check that all volumes have the same shape and orientation
    if prec is None:
        mat = [v.affine[:3,:3].tolist() for v in vols]  
    else:
        mat = [np.around(v.affine[:3,:3], prec).tolist() for v in vols]
    mat = [x for i, x in enumerate(mat) if i==mat.index(x)]
    if len(mat) > 1:
        raise ValueError(
            "Volumes with different orientations or voxel sizes cannot be "
            "concatenated."
        )
    mat = vols[0].affine[:3,:3]

    if not move:
        # Check that all volumes are correctly aligned.
        pos = [v.affine[:3,3] for v in vols]
        concat_vec = mat[:,axis]
        for i, v in enumerate(vols[:-1]):
            pos_next = pos[i] + concat_vec*v.shape[axis]
            dist = np.linalg.norm(pos[i+1]-pos_next)
            if prec is not None:
                dist = np.around(dist, prec)
            if dist > 0:
                raise ValueError(
                    "Volumes cannot be concatenated. They are not aligned in "
                    "the direction of concatenation. Set move=True if want to "
                    "allow them to move to the correct position."
                )
        
    # Determine concatenation and return new volume
    affine = vols[0].affine
    values = np.concatenate([v.values for v in vols], axis=axis)

    return Volume3D(values, affine)  






