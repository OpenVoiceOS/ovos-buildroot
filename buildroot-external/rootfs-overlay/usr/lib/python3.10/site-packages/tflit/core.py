import numpy as np
import tflite_runtime.interpreter as tflite
from . import util


class Model:
    '''Tflite Model, providing a similar interface to Keras.

    Example:
    >>> model = tflit.Model('path/to/model.tflite', batch_size=32, num_threads=3)
    >>> model.summary()
    >>> model.predict(X)  # if multiple inputs, X is a list, otherwise, just the array.

    Alternate Prediction Methods:
    >>> # predict with arbitrary batch size
    >>> model.predict(np.ones([121, 128, 128, 1]))
    >>> # Output: array([121, 10])  # output matches batch size

    >>> # predict with exact batch size
    >>> model.predict_batch(np.ones([32, 128, 128, 1]))  # must match batch size
    >>> # Output: array([32, 10])  # output matches batch size

    >>> # predict each batch but keep them separate
    >>> model.predict_each_batch(np.ones([68, 128, 128, 1]))
    >>> # Output: [array([32, 10]), array([32, 10]), array([4, 10])]  # output matches batch size

    >>> # predict while yielding over batches
    >>> for x in model.predict_each_batch(np.ones([68, 128, 128, 1])):
    ...     print(x.shape)
    >>> # Output: [array([32, 10]), array([32, 10]), array([4, 10])]  # output matches batch size

    >>> # predict while yielding over batches (manually)
    >>> for x in self.as_batches(X, multi_output=True):  # set multi-out/input to prevent squeezing
    ...     out = self.predict_batch(x, multi_input=True)
    >>> # Output: [array([32, 10]), array([32, 10]), array([4, 10])]  # output matches batch size
    '''
    input_details = ()
    output_details = ()
    multi_input = multi_output = True
    _input_idxs = ()
    _output_idxs = ()
    def __init__(self, model_path=None, inputs=None, outputs=None, batch_size=None, num_threads=None, model_content=None, allocate=True, **kw):
        assert model_path or model_content
        self.model_path = model_path
        self.interpreter = tflite.Interpreter(model_path, num_threads=num_threads, model_content=model_content, **kw)
        self._given_input_idxs = inputs
        self._given_output_idxs = outputs
        if allocate:
            self.reallocate()

        # update batch if provided
        if batch_size:
            self.set_batch_size(batch_size)

    def __repr__(self):
        return '{}( {!r}, in={} out={} )'.format(
            self.__class__.__name__, self.model_path,
            self.input_shape, self.output_shape)

    # def resize_input(self, size, index=0, allocate=True):
    #     if isinstance(size, int):
    #         size = (size,) + self.input_shapes[index][1:]
    #     self.interpreter.resize_tensor_input(index, size)
    #     if allocate:
    #         self.reallocate()

    def reallocate(self):
        '''Will reallocate tensors and refresh tensor details.'''
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # convert user inputted indexes to the actual tensor indexes
        self._input_idxs, self.multi_input = util.get_auto_index(
            self._given_input_idxs, self.input_details)
        self._output_idxs, self.multi_output = util.get_auto_index(
            self._given_output_idxs, self.output_details)

    def set_batch_size(self, batch_size, allocate=True):
        '''Change the batch size of the model.'''
        # set batch for inputs
        for d in self.input_details:
            self.interpreter.resize_tensor_input(
                d['index'], [batch_size] + list(d['shape'][1:]))

        # set batch for outputs
        for d in self.output_details:
            self.interpreter.resize_tensor_input(
                d['index'], [batch_size] + list(d['shape'][1:]))

        # apply changes
        if allocate:
            self.reallocate()
            assert self.batch_size == batch_size, 'batch size expected to be {}, but was {}.'.format(batch_size, self.batch_size)

    def reset(self):
        '''Reset all interpreter variables.'''
        self.interpreter.reset_all_variables()

    # def __getitem__(self, i):
    #     '''Returns a numpy view pointing to the tensor buffer.'''
    #     return self.interpreter.tensor(self._input_idxs[i] if isinstance(i, int) else i)()

    # def get(self, index):
    #     '''Get a copy of the tensor buffer'''
    #     return self.interpreter.get_tensor(index)

    def input(self, i):
        '''Returns a numpy view pointing to the input tensor buffer.'''
        return self.interpreter.tensor(self._input_idxs[i] if isinstance(i, int) else i)()

    def output(self, i):
        '''Returns a numpy view pointing to the output tensor buffer.'''
        return self.interpreter.tensor(self._output_idxs[i] if isinstance(i, int) else i)()

    def input_value(self, i=0):
        '''Returns a copy of the input tensor value.'''
        return self.interpreter.get_tensor(self._input_idxs[i] if isinstance(i, int) else i)

    def output_value(self, i=0):
        '''Returns a copy of the output tensor value.'''
        return self.interpreter.get_tensor(self._output_idxs[i] if isinstance(i, int) else i)

    ##############
    # Model
    ##############

    def __call__(self, X, *a, **kw):
        '''Call predict on data. Alias for model.predict(...).'''
        return self.predict(X, *a, **kw)

    def predict_batch(self, X, multi_input=None, multi_output=None, add_batch=False):
        '''Predict a single batch.'''
        # set inputs
        X = self._check_inputs(X, multi_input)
        for i, idx in self._input_idxs:
            self.interpreter.set_tensor(idx, X[i][None] if add_batch else X[i])

        # compute outputs
        self.interpreter.invoke()

        # get outputs
        return self._check_outputs([
            self.interpreter.get_tensor(idx)
            for i, idx in self._output_idxs], multi_output)

    def predict(self, X, multi_input=None, multi_output=None):
        '''Predict data.'''
        return self._check_outputs([
            np.concatenate(x) for x in zip(*self.predict_each_batch(
                X, multi_input=multi_input, multi_output=True))
        ], multi=multi_output)

    def as_batches(self, X, multi_input=None, multi_output=None):
        '''Yield X in batches.'''
        X = self._check_inputs(X, multi_input)
        batch_size = self.batch_size

        # check that there's only one batch size
        batch_sizes = [len(x) for x in X]
        if len(set(batch_sizes)) != 1:
            raise ValueError(
                'Expected a single batch size. Got {}.'.format(batch_sizes))

        for i in range(0, len(X[0]), batch_size):
            xi = [x[i:i + batch_size] for x in X]
            yield xi if multi_output or len(xi) != 1 else xi[0]

    def predict_each_batch(self, X, multi_input=None, multi_output=None):
        '''Predict and yield each batch.'''
        # NOTE: multi=True so we don't squeeze
        for x in self.as_batches(X, multi_input=multi_input, multi_output=True):
            yield self.predict_batch(x, True, multi_output)


    def _check_inputs(self, X, multi=None, cast=True):
        # coerce inputs to be a list
        multi = self.multi_input if multi is None else multi
        X = X if multi else [X]
        if cast:
            dtypes = self.input_dtypes
            for i, dtype in enumerate(dtypes):
                X[i] = np.asarray(X[i], dtype=dtype)
        return X

    def _check_outputs(self, Y, multi=None):
        # return either a single array or list of arrays depending on
        # single/multi output
        multi = self.multi_output if multi is None else multi
        return Y if multi else Y[0] if len(Y) else None

    ##############
    # Info
    ##############

    # names

    @property
    def input_names(self):
        '''The input names. This is a list of strings.'''
        return [d['name'] for d in self.input_details]

    @property
    def output_names(self):
        '''The output names. This is a list of strings. This may not be correct
        depending on how the model was exported.'''
        return [d['name'] for d in self.output_details]

    # dtypes

    @property
    def input_dtypes(self):
        '''The input dtypes. This is a list of np.dtype objects.'''
        return [d['dtype'] for d in self.input_details]

    @property
    def output_dtypes(self):
        '''The output dtypes. This is a list of np.dtype objects.'''
        return [d['dtype'] for d in self.output_details]

    @property
    def dtype(self):
        '''The model dtype. This will take the first dtype it finds for the inputs/outputs.'''
        return next(iter(self.input_dtypes + self.output_dtypes), None)

    # shapes

    @property
    def input_shapes(self):
        '''The input shapes. This is a list of tuples.'''
        return [tuple(d['shape']) for d in self.input_details]

    @property
    def output_shapes(self):
        '''The output shapes. This is a list of tuples.'''
        return [tuple(d['shape']) for d in self.output_details]

    # shape

    @property
    def input_shape(self):
        '''The input shape. If there are more than one input, this will be a list of tuples,
        otherwise it'll be a single tuple.'''
        shape = self.input_shapes
        return shape[0] if len(shape) == 1 else shape

    @property
    def output_shape(self):
        '''The output shape. If there are more than one output, this will be a list of tuples,
        otherwise it'll be a single tuple.'''
        shape = self.output_shapes
        return shape[0] if len(shape) == 1 else shape

    @property
    def batch_size(self):
        '''The current batch size. If there are more than one input, it will look at the first one.'''
        shapes = self.input_shapes
        return shapes[0][0] if shapes else None

    # print

    def summary(self):
        print(util.add_border('\n'.join([
            str(self),
            '', '-- Input details --',
            util.format_details(self.input_details),
            '', '-- Output details --',
            util.format_details(self.output_details),
        ]), ch='.'))
