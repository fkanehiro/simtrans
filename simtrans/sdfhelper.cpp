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

PyMODINIT_FUNC
initsimtranssdfhelper(void)
{
    PyObject *m;
    m = Py_InitModule3("simtranssdfhelper", methods, ext_doc);
    PyModule_AddStringConstant(m, "SDFVERSION", sdf::SDF::version.c_str());
}
