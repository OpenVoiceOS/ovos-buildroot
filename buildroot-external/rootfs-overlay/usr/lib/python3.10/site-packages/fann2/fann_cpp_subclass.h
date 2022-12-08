#ifndef FANN_CPP_SUBCLASS_H_INCLUDED
#define FANN_CPP_SUBCLASS_H_INCLUDED

#include <stdarg.h>
#include <string>
#include <fann_cpp.h>

#include <iostream>
/* Namespace: FANN
    The FANN namespace groups the C++ wrapper definitions */
namespace FANN
{
	
    template <typename T>
    class helper_array
    {
    	public:
            helper_array()
            {
                array=0;
                array_len=0;
		can_delete=true;
            }
            void set (T * array, unsigned int len)
            {
                this->array=array;
                this->array_len=array_len;
            }
            T* array;
            unsigned int array_len;
	    bool can_delete;
    };
    
    template <typename T>
    class helper_array_array
    {
        public:
            helper_array_array()
            {
                arrays=0;
                array_len=0;
                array_num=0;
                can_delete=false;
            }
            void set (T ** arrays, unsigned int len, unsigned int nun)
            {
                this->arrays=arrays;
                this->array_len=array_len;
                this->array_num=array_num;
            }
            T** arrays;
            unsigned int array_len;
            unsigned int array_num;
            bool can_delete;
    };
	
    /* Forward declaration of class neural_net and training_data */
    class Neural_net;
    class Training_data;


    /*************************************************************************/

    /* Class: training_data

        Encapsulation of a training data set <struct fann_train_data> and
        associated C API functions.
    */
    class Training_data : public training_data
    {
    public:
        /* Constructor: training_data
        
            Default constructor creates an empty neural net.
            Use <read_train_from_file>, <set_train_data> or <create_train_from_callback> to initialize.
        */
        Training_data() : training_data()
        {
        }

        /* Constructor: training_data
        
            Copy constructor constructs a copy of the training data.
            Corresponds to the C API <fann_duplicate_train_data> function.
        */
        Training_data(const Training_data &data)
        {
            destroy_train();
            if (data.train_data != NULL)
            {
                train_data = fann_duplicate_train_data(data.train_data);
            }
        }

        /* Destructor: ~training_data

            Provides automatic cleanup of data.
            Define USE_VIRTUAL_DESTRUCTOR if you need the destructor to be virtual.

            See also:
                <destroy>
        */
#ifdef USE_VIRTUAL_DESTRUCTOR
        virtual
#endif
        ~Training_data()
        {
            destroy_train();
        }



        /* Grant access to the encapsulated data since many situations
            and applications creates the data from sources other than files
            or uses the training data for testing and related functions */

        /* Method: get_input
        
            Returns:
                A pointer to the array of input training data

            See also:
                <get_output>, <set_train_data>
        */
        helper_array_array<fann_type>* get_input()
        {
            if (train_data == NULL)
            {
                return NULL;
            }
            else
            {
                helper_array_array<fann_type>* ret = new helper_array_array<fann_type>;
                
                ret->arrays=train_data->input;
                ret->array_num=train_data->num_data;
                ret->array_len=train_data->num_input;
		ret->can_delete=false;
                return ret;
            }
        }

        /* Method: get_output
        
            Returns:
                A pointer to the array of output training data

            See also:
                <get_input>, <set_train_data>
        */

        helper_array_array<fann_type>* get_output()
        {
            if (train_data == NULL)
            {
                return NULL;
            }
            else
            {
                helper_array_array<fann_type>* ret = new helper_array_array<fann_type>;
                
                ret->arrays=train_data->output;
                ret->array_num=train_data->num_data;
                ret->array_len=train_data->num_output;
		ret->can_delete=false;
                return ret;
            }
        }


        /* Method: set_train_data

            Set the training data to the input and output data provided.

            A copy of the data is made so there are no restrictions on the
            allocation of the input/output data and the caller is responsible
            for the deallocation of the data pointed to by input and output.
            
            See also:
                <get_input>, <get_output>
        */

        void set_train_data(helper_array_array< fann_type >* input,
            helper_array_array< fann_type >* output)
        {
            if (input->array_num!=output->array_num) 
            {
                std::cerr<<"Error: input and output must have the same dimension!"<<std::endl;
                return;
            }
            input->can_delete=true;
            output->can_delete=true;
            
	    training_data::set_train_data(input->array_num, input->array_len, input->arrays, output->array_len, output->arrays);
        }  


    };

    /*************************************************************************/

    /* Class: Neural_net

        Encapsulation of a neural network <struct fann> and
        associated C API functions.
    */
    class Neural_net : public neural_net
    {
    public:
        /* Constructor: neural_net
        
            Default constructor creates an empty neural net.
            Use one of the create functions to create the neural network.

            See also:
		        <create_standard>, <create_sparse>, <create_shortcut>,
		        <create_standard_array>, <create_sparse_array>, <create_shortcut_array>
        */
        Neural_net() : neural_net()
        {
        }

        /* Destructor: ~neural_net

            Provides automatic cleanup of data.
            Define USE_VIRTUAL_DESTRUCTOR if you need the destructor to be virtual.

            See also:
                <destroy>
        */
#ifdef USE_VIRTUAL_DESTRUCTOR
        virtual
#endif
        ~Neural_net()
        {
            destroy();
        }


        /* Method: create_standard_array

           Just like <create_standard>, but with an array of layer sizes
           instead of individual parameters.

	        See also:
		        <create_standard>, <create_sparse>, <create_shortcut>,
		        <fann_create_standard>

	        This function appears in FANN >= 2.0.0.
        */ 

        bool create_standard_array( helper_array<unsigned int>* layers)
        {
            return neural_net::create_standard_array( layers->array_len, layers->array);
        }

        /* Method: create_sparse_array
           Just like <create_sparse>, but with an array of layer sizes
           instead of individual parameters.

           See <create_sparse> for a description of the parameters.

	        See also:
		        <create_standard>, <create_sparse>, <create_shortcut>,
		        <fann_create_sparse_array>

	        This function appears in FANN >= 2.0.0.
        */

        bool create_sparse_array(float connection_rate,
            helper_array<unsigned int>* layers)
         {
            return neural_net::create_sparse_array( connection_rate, layers->array_len, layers->array);
         }

        /* Method: create_shortcut_array

           Just like <create_shortcut>, but with an array of layer sizes
           instead of individual parameters.

	        See <create_standard_array> for a description of the parameters.

	        See also:
		        <create_standard>, <create_sparse>, <create_shortcut>,
		        <fann_create_shortcut_array>

	        This function appears in FANN >= 2.0.0.
        */

        bool create_shortcut_array( helper_array<unsigned int>* layers)
        {
            return neural_net::create_shortcut_array( layers->array_len, layers->array);
        }

        /* Method: run

	        Will run input through the neural network, returning an array of outputs, the number of which being 
	        equal to the number of neurons in the output layer.

	        See also:
		        <test>, <fann_run>

	        This function appears in FANN >= 1.0.0.
        */ 

         helper_array<fann_type>* run(helper_array<fann_type> *input)
         {
            if (ann == NULL && input->array_len!=ann->num_input)
            {
                return NULL;
            }
            helper_array<fann_type>* res= new helper_array<fann_type>;
            res->array=fann_run(ann, input->array);
            res->array_len=ann->num_output;
            res->can_delete=false;
            return res;
         }



#ifndef FIXEDFANN
        /* Method: train

           Train one iteration with a set of inputs, and a set of desired outputs.
           This training is always incremental training (see <FANN::training_algorithm_enum>),
           since only one pattern is presented.
           
           Parameters:
   	        ann - The neural network structure
   	        input - an array of inputs. This array must be exactly <fann_get_num_input> long.
   	        desired_output - an array of desired outputs. This array must be exactly <fann_get_num_output> long.
           	
   	        See also:
   		        <train_on_data>, <train_epoch>, <fann_train>
           	
   	        This function appears in FANN >= 1.0.0.
         */

        void train(helper_array<fann_type> *input, helper_array<fann_type> *desired_output)
        {
            if (ann != NULL && input->array_len==ann->num_input && desired_output->array_len==ann->num_output)
            {
                fann_train(ann, input->array, desired_output->array);
            }
        }

#endif /* NOT FIXEDFANN */

        /* Method: test

           Test with a set of inputs, and a set of desired outputs.
           This operation updates the mean square error, but does not
           change the network in any way.
           
           See also:
   		        <test_data>, <train>, <fann_test>
           
           This function appears in FANN >= 1.0.0.
        */ 

         helper_array<fann_type>* test(helper_array<fann_type> *input, helper_array<fann_type>* desired_output)
         {
            if (ann == NULL)
            {
                return NULL;
            }
            helper_array<fann_type>* res= new helper_array<fann_type>;
            res->array=fann_test(ann, input->array, desired_output->array);
            res->array_len=ann->num_output;
            res->can_delete=false;
            return res;
        }


        /*************************************************************************************************************/


        /* Method: get_layer_array

            Get the number of neurons in each layer in the network.

            Bias is not included so the layers match the create methods.

            The layers array must be preallocated to at least
            sizeof(unsigned int) * get_num_layers() long.

            See also:
                <fann_get_layer_array>

           This function appears in FANN >= 2.1.0
        */

        void get_layer_array(helper_array<unsigned int>* ARGOUT)
        {
            if (ann != NULL)
            {
                ARGOUT->array_len = fann_get_num_layers(ann);
                ARGOUT->array = (unsigned int*) malloc(sizeof(unsigned int)* 
                        ARGOUT->array_len);
                fann_get_layer_array(ann, ARGOUT->array);
            }
        }

        /* Method: get_bias_array

            Get the number of bias in each layer in the network.

            The bias array must be preallocated to at least
            sizeof(unsigned int) * get_num_layers() long.

            See also:
                <fann_get_bias_array>

            This function appears in FANN >= 2.1.0
        */
        void get_bias_array(helper_array<unsigned int>* ARGOUT)
        {
            if (ann != NULL)
            {
                ARGOUT->array_len = fann_get_num_layers(ann);
                ARGOUT->array = (unsigned int*) malloc(sizeof(unsigned int)* 
                        ARGOUT->array_len);
                fann_get_bias_array(ann, ARGOUT->array);
            }
        }

        /* Method: get_connection_array

            Get the connections in the network.

            The connections array must be preallocated to at least
            sizeof(struct fann_connection) * get_total_connections() long.

            See also:
                <fann_get_connection_array>

           This function appears in FANN >= 2.1.0
        */
	
        void get_connection_array(helper_array<connection> *ARGOUT)
        {
            if (ann != NULL)
            {
                ARGOUT->array_len = fann_get_total_connections(ann); 
                ARGOUT->array = (connection*) malloc(sizeof(connection)* 
                        ARGOUT->array_len);
                fann_get_connection_array(ann, ARGOUT->array);
            }
        }
        /* Method: set_weight_array

            Set connections in the network.

            Only the weights can be changed, connections and weights are ignored
            if they do not already exist in the network.

            The array must have sizeof(struct fann_connection) * num_connections size.

            See also:
                <fann_set_weight_array>

           This function appears in FANN >= 2.1.0
        */
        void set_weight_array(helper_array<connection> *connections)
        {
            if (ann != NULL)
            {
                fann_set_weight_array(ann, connections->array, connections->array_len);
            }
        }

        /*********************************************************************/

#ifdef TODO
        /* Method: get_cascade_activation_functions

           The cascade activation functions array is an array of the different activation functions used by
           the candidates. 
           
           See <get_cascade_num_candidates> for a description of which candidate neurons will be 
           generated by this array.
           
           See also:
   		        <get_cascade_activation_functions_count>, <set_cascade_activation_functions>,
   		        <FANN::activation_function_enum>

	        This function appears in FANN >= 2.0.0.
         */
        activation_function_enum * get_cascade_activation_functions()
        {
            enum fann_activationfunc_enum *activation_functions = NULL;
            if (ann != NULL)
            {
                activation_functions = fann_get_cascade_activation_functions(ann);
            }
            return reinterpret_cast<activation_function_enum *>(activation_functions);
        }

        /* Method: set_cascade_activation_functions

           Sets the array of cascade candidate activation functions. The array must be just as long
           as defined by the count.

           See <get_cascade_num_candidates> for a description of which candidate neurons will be 
           generated by this array.

           See also:
   		        <get_cascade_activation_steepnesses_count>, <get_cascade_activation_steepnesses>,
                <fann_set_cascade_activation_functions>

	        This function appears in FANN >= 2.0.0.
         */
        void set_cascade_activation_functions(activation_function_enum *cascade_activation_functions,
            unsigned int cascade_activation_functions_count)
        {
            if (ann != NULL)
            {
                fann_set_cascade_activation_functions(ann,
                    reinterpret_cast<enum fann_activationfunc_enum *>(cascade_activation_functions),
                    cascade_activation_functions_count);
            }
        }
#endif
        /* Method: get_cascade_activation_steepnesses

           The cascade activation steepnesses array is an array of the different activation functions used by
           the candidates.

           See <get_cascade_num_candidates> for a description of which candidate neurons will be 
           generated by this array.

           The default activation steepnesses is {0.25, 0.50, 0.75, 1.00}

           See also:
   		        <set_cascade_activation_steepnesses>, <get_cascade_activation_steepnesses_count>,
                <fann_get_cascade_activation_steepnesses>

	        This function appears in FANN >= 2.0.0.
         */
        helper_array<fann_type> *get_cascade_activation_steepnesses()
        {
            helper_array<fann_type> *activation_steepnesses = NULL;
            if (ann != NULL)
            {
                activation_steepnesses->array_len = fann_get_cascade_activation_steepnesses_count(ann);
                activation_steepnesses->array = fann_get_cascade_activation_steepnesses(ann);
            }
            return activation_steepnesses;
        }																

        /* Method: set_cascade_activation_steepnesses

           Sets the array of cascade candidate activation steepnesses. The array must be just as long
           as defined by the count.

           See <get_cascade_num_candidates> for a description of which candidate neurons will be 
           generated by this array.

           See also:
   		        <get_cascade_activation_steepnesses>, <get_cascade_activation_steepnesses_count>,
                <fann_set_cascade_activation_steepnesses>

	        This function appears in FANN >= 2.0.0.
         */
        void set_cascade_activation_steepnesses(helper_array<fann_type> *cascade_activation_steepnesses)
        {
            if (ann != NULL)
            {
                fann_set_cascade_activation_steepnesses(ann,
                    cascade_activation_steepnesses->array, cascade_activation_steepnesses->array_len);
            }
        }


    };

    /*************************************************************************/
};

#endif /* FANN_CPP_SUBCLASS_H_INCLUDED */
