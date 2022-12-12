/* File : fann.i */
%module libfann

%include "typemaps.i"
%include "stl.i"

%{
#include "doublefann.h"
#include "fann_io.h"
#include "fann_train.h"
#include "fann_data.h"
#include "fann_cascade.h"
#include "fann_error.h"
#include "fann_activation.h"
#include "fann_cpp_subclass.h"
%}

%define HELPER_ARRAY_TEMPLATE( templ , T, GetFunc, SetFunc, cast) 
    %typemap(in) templ<T> *  (templ<T> temp){
        // templ<T>* type_map in
        int i;
        if (!PySequence_Check($input)) {
            PyErr_SetString(PyExc_ValueError,"Expected a sequence");
            SWIG_fail;
        }
        if (PySequence_Length($input) == 0) {
            PyErr_SetString(PyExc_ValueError,"Size mismatch. Expected some elements");
            SWIG_fail;
        }
        $1=&temp;
        $1->array_len=PySequence_Length($input);
        $1->array = (T *) malloc($1->array_len*sizeof(T));
        for (i = 0; i < PySequence_Length($input); i++) {
            PyObject *o = PySequence_GetItem($input,i);
            if (PyNumber_Check(o)) {
                $1->array[i] = (T) GetFunc(o);
            } else {
                PyErr_SetString(PyExc_ValueError,"Sequence elements must be numbers");      
                Py_DECREF(o);
                SWIG_fail;
            }
            Py_DECREF(o);
        }
    }
%typemap(freearg) templ<T>* {
    // templ<T>* type_map freearg
    if ($1 && $1->array && $1->can_delete) 
    {	
        free($1->array);
    }
}

%typemap(out) templ<T>* {
    // templ* type_map out
    $result= PyList_New( $1->array_len );
    for (unsigned int i = 0; i < $1->array_len; i++) 
    {
        PyObject *o = SetFunc( (cast) $1->array[i]);
        PyList_SetItem($result,i,o);
    }
    if ($1 && $1->array && $1->can_delete) 
    {	
        free($1->array);
    }
    if ($1) delete $1;
  
}

%typemap(argout)  templ<T>* ARGOUT{
    // templ* type_map out
    $result= PyList_New( $1->array_len );
    for (unsigned int i = 0; i < $1->array_len; i++) 
    {
        PyObject *o = SetFunc( (cast) $1->array[i]);
        PyList_SetItem($result,i,o);
    }
    if ($1 && $1->array && $1->can_delete) 
    {	
        free($1->array);
    }
    if ($1) delete $1;
}

%enddef

%define HELPER_ARRAY_ARRAY_TEMPLATE(templ, T,  GetFunc, SetFunc, cast) 
%typemap(in) templ< T >* ( templ<T> temp) {
    // templ<T>* type_map
    unsigned int i;  
    unsigned int j;
    unsigned int dim;
    unsigned int num;
    if (!PySequence_Check($input)) {
        PyErr_SetString(PyExc_ValueError,"Expected a sequence");
        SWIG_fail;
    }
    if (PySequence_Length($input) == 0) {
        PyErr_SetString(PyExc_ValueError,"Size mismatch. Expected some elements");
        SWIG_fail;
    }
    $1=&temp;
    num=PySequence_Length($input);
    $1->array_num=num;
    
    PyObject* o0=PySequence_GetItem($input,0);
    if (!PySequence_Check(o0)) {
        PyErr_SetString(PyExc_ValueError,"Expected an inner sequence");
        Py_DECREF(o0);
        SWIG_fail;
    }
    dim=PySequence_Length(o0);
    Py_DECREF(o0);
    
    $1->array_len=dim;
    $1->arrays = (T **) calloc(num,sizeof(T*));
  
    for (j = 0; j< num; j++)
    {
        PyObject* o1=PySequence_GetItem($input,j);
        if (!PySequence_Check(o1)) {
            PyErr_SetString(PyExc_ValueError,"Expected an inner sequence");
            Py_DECREF(o1);
            SWIG_fail;
        }
        if ((unsigned int)PySequence_Length(o1) != dim) {
            PyErr_SetString(PyExc_ValueError,"Size mismatch. All items must be of the same size");
            Py_DECREF(o1);
            SWIG_fail;
        }
        $1->arrays[j] = (T*) malloc(dim*sizeof(T));
        for (i = 0; i < dim; i++) {
            PyObject *o = PySequence_GetItem(o1,i);
            if (PyNumber_Check(o)) {
                $1->arrays[j][i] = (T) GetFunc(o);
            } else {
                PyErr_SetString(PyExc_ValueError,"Sequence elements must be numbers");      
                Py_DECREF(o);
                Py_DECREF(o1);
                SWIG_fail;
            }
            Py_DECREF(o);
        }
        Py_DECREF(o1);
    }
}
%typemap(freearg) templ< T >* {
    // templ* type_map freearg
    unsigned int i;
    if ($1 && $1->arrays && $1->can_delete) 
    {
        for (i=0; i < $1->array_num;++i)
        	if ($1->arrays[i]) 
                free($1->arrays[i]);
        free($1->arrays);
    }
}
%typemap(out) templ<T>* {
    // templ* type_map out
    $result= PyList_New( $1->array_num );
    for (unsigned int j = 0; j < $1->array_num; ++j) 
    {
        PyObject *l= PyList_New( $1->array_len );
        PyList_SetItem($result,j,l);
        for (unsigned int i = 0; i < $1->array_len; i++) 
        {
            PyObject *o = SetFunc($1->arrays[j][i] );
            //PyObject *o = SetFunc($1->arrays[i][j] );
            PyList_SetItem(l,i,o);
        }
    }
    unsigned int i;
    if ($1 && $1->arrays && $1->can_delete) 
    {
        for (i=0; i < $1->array_num;++i)
        	if ($1->arrays[i]) 
                free($1->arrays[i]);
        free($1->arrays);
    }
    if ($1) delete $1;
}
%enddef

%import "../include/doublefann.h"
%import "../include/fann.h"
%import "../include/fann_io.h"
%import "../include/fann_train.h"
%import "../include/fann_data.h"
%import "../include/fann_cascade.h"
%import "../include/fann_error.h"
%import "../include/fann_activation.h"

HELPER_ARRAY_TEMPLATE( FANN::helper_array, unsigned int, PyInt_AsLong    , PyInt_FromLong    , long   );
HELPER_ARRAY_TEMPLATE( FANN::helper_array, fann_type   , PyFloat_AsDouble, PyFloat_FromDouble, double );

HELPER_ARRAY_ARRAY_TEMPLATE( FANN::helper_array_array, fann_type   , PyFloat_AsDouble, PyFloat_FromDouble, double );

%rename(neural_net_parent) FANN::neural_net;
%rename(neural_net) FANN::Neural_net;

%rename(training_data_parent) FANN::training_data;
%rename(training_data) FANN::Training_data;

%include "../include/fann_cpp.h"
%include "fann_cpp_subclass.h"

/* ex: set ts=4: set sw=4: set cin */
