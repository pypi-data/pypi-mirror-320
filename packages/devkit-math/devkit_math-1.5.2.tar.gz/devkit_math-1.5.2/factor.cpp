#define PY_SSIZE_T_CLEAN
#include <Python.h>
PyObject* factor_cnt(PyObject* self, PyObject* args)
{
	long x;
	if (!PyArg_ParseTuple(args, "l", &x))
	{
		return nullptr;
	}
    long cnt = 0;
	for (long i = 1; i * i <= x; i++)
    {
        if (x % i == 0)
        {
            cnt += 2;
        }
        if (i * i == x)
        {
            cnt--;
        }
    }
	return PyLong_FromLong(cnt);
}
PyObject* factor_sum(PyObject* self, PyObject* args)
{
	long x;
	if (!PyArg_ParseTuple(args, "l", &x))
	{
		return nullptr;
	}
	long sum = 0;
	for (long i = 1; i * i <= x; i++)
    {
        if (x % i == 0)
        {
            sum += i + x / i;
        }
        if (i * i == x)
        {
            sum -= i;
        }
    }
	return PyLong_FromLong(sum);
}
static PyMethodDef factor_methods[] = {
	{ "factor_cnt", (PyCFunction)factor_cnt, METH_VARARGS, nullptr },
	{ "factor_sum", (PyCFunction)factor_sum, METH_VARARGS, nullptr },
	{ nullptr, nullptr, 0, nullptr }
};
static PyModuleDef factor_module = {
	PyModuleDef_HEAD_INIT,
	"factor",
	nullptr,
	0,
	factor_methods
};
PyMODINIT_FUNC PyInit_factor()
{
	return PyModule_Create(&factor_module);
}

