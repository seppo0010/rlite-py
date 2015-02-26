#include "rlite.h"

static void Rlite_dealloc(hirlite_RliteObject *self);
static int Rlite_init(hirlite_RliteObject *self, PyObject *args, PyObject *kwds);
static PyObject *Rlite_new(PyTypeObject *type, PyObject *args, PyObject *kwds);

static PyMethodDef hirlite_RliteMethods[] = {
    { NULL }  /* Sentinel */
};

PyTypeObject hirlite_RliteType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    MOD_HIRLITE ".Rlite",         /*tp_name*/
    sizeof(hirlite_RliteObject),  /*tp_basicsize*/
    0,                            /*tp_itemsize*/
    (destructor)Rlite_dealloc,    /*tp_dealloc*/
    0,                            /*tp_print*/
    0,                            /*tp_getattr*/
    0,                            /*tp_setattr*/
    0,                            /*tp_compare*/
    0,                            /*tp_repr*/
    0,                            /*tp_as_number*/
    0,                            /*tp_as_sequence*/
    0,                            /*tp_as_mapping*/
    0,                            /*tp_hash */
    0,                            /*tp_call*/
    0,                            /*tp_str*/
    0,                            /*tp_getattro*/
    0,                            /*tp_setattro*/
    0,                            /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "Hirlite protocol reader",    /*tp_doc */
    0,                            /*tp_traverse */
    0,                            /*tp_clear */
    0,                            /*tp_richcompare */
    0,                            /*tp_weaklistoffset */
    0,                            /*tp_iter */
    0,                            /*tp_iternext */
    hirlite_RliteMethods,         /*tp_methods */
    0,                            /*tp_members */
    0,                            /*tp_getset */
    0,                            /*tp_base */
    0,                            /*tp_dict */
    0,                            /*tp_descr_get */
    0,                            /*tp_descr_set */
    0,                            /*tp_dictoffset */
    (initproc)Rlite_init,         /*tp_init */
    0,                            /*tp_alloc */
    Rlite_new,                    /*tp_new */
};

static void Rlite_dealloc(hirlite_RliteObject *self) {
    // rliteReplyRliteFree(self->reader);
    if (self->encoding)
        free(self->encoding);

    ((PyObject *)self)->ob_type->tp_free((PyObject*)self);
}

static int Rlite_init(hirlite_RliteObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = { "path", "encoding", NULL };
    PyObject *encodingObj = NULL;
    char *path = ":memory:";

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|sO", kwlist, &path, &encodingObj))
            return -1;

    if (encodingObj) {
        PyObject *encbytes;
        char *encstr;
        int enclen;

        if (PyUnicode_Check(encodingObj))
            encbytes = PyUnicode_AsASCIIString(encodingObj);
        else
            encbytes = PyObject_Bytes(encodingObj);

        if (encbytes == NULL)
            return -1;

        enclen = PyBytes_Size(encbytes);
        encstr = PyBytes_AsString(encbytes);
        self->encoding = (char*)malloc(enclen+1);
        memcpy(self->encoding, encstr, enclen);
        self->encoding[enclen] = '\0';
        Py_DECREF(encbytes);
    }

    self->context = rliteConnect(path, 0);

    return 0;
}

static PyObject *Rlite_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    hirlite_RliteObject *self;
    self = (hirlite_RliteObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->encoding = NULL;
    }
    return (PyObject*)self;
}
