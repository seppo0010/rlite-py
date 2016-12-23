#include "rlite.h"

static void Rlite_dealloc(hirlite_RliteObject *self);
static int Rlite_init(hirlite_RliteObject *self, PyObject *args, PyObject *kwds);
static PyObject *Rlite_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static PyObject *Rlite_command(hirlite_RliteObject *self, PyObject *args);

static PyMethodDef hirlite_RliteMethods[] = {
    {"command", (PyCFunction)Rlite_command, METH_VARARGS, NULL },
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
    "Hirlite",                    /*tp_doc */
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
    rliteFree(self->context);
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
        Py_ssize_t enclen;

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
        self->context = NULL;
    }
    return (PyObject*)self;
}

static PyObject *createDecodedString(hirlite_RliteObject *self, const char *str, size_t len) {
    PyObject *obj;

    if (self->encoding == NULL) {
        obj = PyBytes_FromStringAndSize(str, len);
    } else {
        obj = PyUnicode_Decode(str, len, self->encoding, NULL);
        if (obj == NULL) {
            if (PyErr_ExceptionMatches(PyExc_ValueError)) {
                /* Ignore encoding and simply return plain string. */
                obj = PyBytes_FromStringAndSize(str, len);
            } else {
                assert(PyErr_ExceptionMatches(PyExc_LookupError));

                /* Return Py_None as placeholder to let the error bubble up and
                 * be used when a full reply in Reader#gets(). */
                obj = Py_None;
                Py_INCREF(obj);
            }

            PyErr_Clear();
        }
    }

    assert(obj != NULL);
    return obj;
}
static PyObject *replyToPyObject(hirlite_RliteObject *self, rliteReply *reply) {
    if (reply->type == RLITE_REPLY_STATUS || reply->type == RLITE_REPLY_STRING) {
        if (reply->type == RLITE_REPLY_STATUS && reply->len == 2 && memcmp(reply->str, "OK", 2) == 0) {
            Py_INCREF(Py_True);
            return Py_True;
        }
        return createDecodedString(self, reply->str, reply->len);
    }
    if (reply->type == RLITE_REPLY_NIL) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    if (reply->type == RLITE_REPLY_INTEGER) {
        return PyLong_FromLongLong(reply->integer);
    }
    if (reply->type == RLITE_REPLY_ERROR) {
        PyObject *obj;

        PyObject *args = Py_BuildValue("(s#)", reply->str, reply->len);
        assert(args != NULL);
        obj = PyObject_CallObject(HIRLITE_STATE->HiErr_Base, args);
        assert(obj != NULL);
        Py_DECREF(args);
        return obj;
    }
    if (reply->type == RLITE_REPLY_ARRAY) {
        PyObject *obj, *element;
        size_t i;
        obj = PyList_New(reply->elements);
        for (i = 0; i < reply->elements; i++) {
            element = replyToPyObject(self, reply->element[i]);
            PyList_SET_ITEM(obj, i, element);
        }
        return obj;
    }
    return NULL;
}

static PyObject *Rlite_command(hirlite_RliteObject *self, PyObject *args) {
    PyObject *object;
    int i, argc;
    char **argv;
    size_t *argvlen;
    PyObject *bytes;
    char *str;
    size_t len;
    rliteReply *reply;

    argc = (int)PyTuple_Size(args);
    argv = malloc(sizeof(char *) * argc);
    if (!argv)
        return NULL;
    argvlen = malloc(sizeof(size_t) * argc);
    if (!argvlen) {
        free(argv);
        return NULL;
    }

    for (i = 0; i < argc; i++) {
        object = PyTuple_GetItem(args, i);
        if (PyUnicode_Check(object))
            bytes = PyUnicode_AsASCIIString(object);
        else
            bytes = PyObject_Bytes(object);

        if (bytes == NULL)
            return NULL;

        argvlen[i] = len = PyBytes_Size(bytes);
        str = PyBytes_AsString(bytes);
        argv[i] = (char*)malloc(len+1);
        memcpy(argv[i], str, len);
        argv[i][len] = '\0';
        Py_DECREF(bytes);
    }

    reply = rliteCommandArgv(self->context, argc, argv, argvlen);
    object = replyToPyObject(self, reply);

    for (i = 0; i < argc; i++) {
        free(argv[i]);
    }
    free(argv);
    free(argvlen);
    rliteFreeReplyObject(reply);

    return object;
}
