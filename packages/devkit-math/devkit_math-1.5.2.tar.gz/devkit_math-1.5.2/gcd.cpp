#define PY_SSIZE_T_CLEAN
#include <Python.h>
PyObject* gcd(PyObject* self, PyObject* args)
{
	long x, y;
	if (!PyArg_ParseTuple(args, "ll", &x, &y))
	{
		return nullptr;
	}
	while (y > 0)
	{
		long t = x;
		x = y;
		y = t % y;
	}
	return PyLong_FromLong(x);
}
PyObject* lcm(PyObject* self, PyObject* args)
{
	long x, y;
	if (!PyArg_ParseTuple(args, "ll", &x, &y))
	{
		return nullptr;
	}
	long tx = x, ty = y;
	while (y > 0)
	{
		long t = x;
		x = y;
		y = t % y;
	}
	return PyLong_FromLong(tx / x * ty);
}
static PyMethodDef gcd_methods[] = {
	{ "gcd", (PyCFunction)gcd, METH_VARARGS, nullptr },
	{ "lcm", (PyCFunction)lcm, METH_VARARGS, nullptr },
	{ nullptr, nullptr, 0, nullptr }
};
static PyModuleDef gcd_module = {
	PyModuleDef_HEAD_INIT,
	"gcd",
	nullptr,
	0,
	gcd_methods
};
PyMODINIT_FUNC PyInit_gcd()
{
	return PyModule_Create(&gcd_module);
}

