#include <Python.h>
#include <string>
#include <sdf/sdf.hh>

static PyObject *
filter(PyObject *self, PyObject *args)
{
    const char *filename;

    if (!PyArg_ParseTuple(args, "s", &filename))
        return NULL;

    sdf::SDFPtr sdf(new sdf::SDF());
    sdf::init(sdf);
    
    char* homePath = getenv("HOME");
    std::string home = homePath;
    sdf::addURIPath("model://", home + "/.gazebo/models");
    
    if (!sdf::readFile(filename, sdf))
      return NULL;
    
    std::string out = sdf->ToString();
    
    return Py_BuildValue("s", out.c_str());
}

static char ext_doc[] = "sdformat helper module\n";

static PyMethodDef methods[] = {
    {"filter", filter, METH_VARARGS, "filter SDF or URDF input"},
    {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "simtranssdfhelper",
    ext_doc,
    -1,
    methods
};
#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC
PyInit_simtranssdfhelper(void)
#else
PyMODINIT_FUNC
initsimtranssdfhelper(void)
#endif
{
    PyObject *m;
#if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&module);
#else
    m = Py_InitModule("simtranssdfhelper", methods);
#endif
    PyModule_AddStringConstant(m, "SDFVERSION", sdf::SDF::Version().c_str());
#if PY_MAJOR_VERSION >= 3
    return m;
#endif
}
