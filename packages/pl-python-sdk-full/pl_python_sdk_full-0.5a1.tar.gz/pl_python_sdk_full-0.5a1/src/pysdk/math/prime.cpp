#define PY_SSIZE_T_CLEAN
#include <Python.h>
PyObject* isprime(PyObject* self, PyObject* args)
{
	long x;
	if (!PyArg_ParseTuple(args, "l", &x))
	{
		return nullptr;
	}
	for (int i = 2; i * i <= x; i++)
	{
		if (x % i == 0)
		{
			return PyBool_FromLong(0);
		}
	}
	return PyBool_FromLong(x > 1);
}
static PyMethodDef prime_methods[] = {
	{ "isprime", (PyCFunction)isprime, METH_VARARGS, nullptr },
	{ nullptr, nullptr, 0, nullptr }
};
static PyModuleDef prime_module = {
	PyModuleDef_HEAD_INIT,
	"prime",
	nullptr,
	0,
	prime_methods
};
PyMODINIT_FUNC PyInit_prime()
{
	return PyModule_Create(&prime_module);
}

