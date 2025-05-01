    #include <boost/python.hpp>
    #include "component/g3t1_3/G3T1_3.hpp"

    char** convert_to_char_array(const boost::python::list& py_list) {
        int argc = len(py_list);
        char** argv = new char*[argc + 1]; 

        for (int i = 0; i < argc; ++i) {
            std::string item = boost::python::extract<std::string>(py_list[i]);
            argv[i] = new char[item.size() + 1];  
            std::strcpy(argv[i], item.c_str());  
        }
        
        argv[argc] = nullptr;  

        return argv;
    }

   char** create_g3t1_3(const boost::python::list& py_list) {
            char** argv = convert_to_char_array(py_list);

            return argv;
        }

    boost::shared_ptr<G3T1_3> create_g3t1_3_instance(int arg, const boost::python::list& py_list, const std::string& some_string) {
    int argc = len(py_list);
    char** argv = new char*[argc];

    for (int i = 0; i < argc; ++i) {
        std::string item = boost::python::extract<std::string>(py_list[i]);
        argv[i] = new char[item.size() + 1];
        std::strcpy(argv[i], item.c_str());
    }
    
    boost::shared_ptr<G3T1_3> instance(new G3T1_3(argc, argv, some_string));

    return instance;
}

    BOOST_PYTHON_MODULE(sensor_module)
    {
        using namespace boost::python;
        class_<G3T1_3, boost::shared_ptr<G3T1_3>, boost::noncopyable>("G3T1_3", no_init)
            .def("setUp", &G3T1_3::setUp)
            .def("collect", &G3T1_3::collect)
            .def("process", &G3T1_3::process)
            .def("transfer", &G3T1_3::transfer);

        def("create_g3t1_3_instance", create_g3t1_3_instance);
    }
