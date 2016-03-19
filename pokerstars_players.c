#include <Python.h>
#include <math.h>

int row_match(PyObject *row_a, PyObject *row_b, int j, int j_lim){
	while (j <= j_lim){
		long w = PyLong_AsLong(PySequence_GetItem(row_a, j));
		long i = PyLong_AsLong(PySequence_GetItem(row_b, j));
		if (w != i){
			return 0;
		};
		j++;
	};
	return 1;
}

int image_match(PyObject *window, PyObject *image, int row, int col, 
		int height, int width, int tolerance){
	int i = 0;
	int j = 0;
	int errs = 0;
	
	while (i < height){
		j = 0;
		PyObject *w_row = PySequence_GetItem(window, i+row);
		PyObject *i_row = PySequence_GetItem(image, i);
// 		printf("window row: %i\n", i+row);
		while (j < width){
			long w_val = PyLong_AsLong(PySequence_GetItem(w_row, j+col));
			long i_val = PyLong_AsLong(PySequence_GetItem(i_row, j));
// 			printf("w_val: %ld, im_val: %ld\n", w_val, i_val);
			if (w_val != i_val){
				errs++;
				if (errs > tolerance){
					Py_DECREF(w_row);
					Py_DECREF(i_row);
					return 0;
				};
			};
			j++;
		};
		i++;
		Py_DECREF(w_row);
		Py_DECREF(i_row);
	};

	return 1;
}

static PyObject *player_number(PyObject *self, PyObject *args){
	PyObject *window;
	PyObject *image;
	int tolerance;
	
	if (!PyArg_ParseTuple(args, "OOi", &window, &image, &tolerance)){
		return NULL;		
	}
	
	int w_shape[2];
	int i_shape[2];
	PyObject *w_shape_obj = PyObject_GetAttrString(window, "shape");
	PyObject *i_shape_obj = PyObject_GetAttrString(image, "shape");
	PyArg_ParseTuple(w_shape_obj, "ii", &w_shape[0], &w_shape[1]);
	PyArg_ParseTuple(i_shape_obj, "ii", &i_shape[0], &i_shape[1]);
	Py_DECREF(w_shape_obj);
	Py_DECREF(i_shape_obj);
	
	int i = 0;
	int j = 0;
	int players = 0;
	while (i <= (w_shape[0] - i_shape[0])){
		j = 0;
		while (j <= (w_shape[1] - i_shape[1])){
			if (image_match(window, image, i, j, i_shape[0], i_shape[1], tolerance) == 1){
				j = j + i_shape[1];
				players++;
			};
			j++;
		};
		i++;
	};
	
	return Py_BuildValue("i", players);
}

/*  define functions in module */
static PyMethodDef MMs[] =
{
	{"player_number", player_number, METH_VARARGS, "get number of players"},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef MM =
{
    PyModuleDef_HEAD_INIT,
    "pokerstars_players", /* name of module */
    "",          /* module documentation, may be NULL */
    -1,          /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    MMs
};

PyMODINIT_FUNC PyInit_pokerstars_players(void)
{
    return PyModule_Create(&MM);
}