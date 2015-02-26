#include "hirlite.h"
#include "rlite.h"

#if IS_PY3K
static int hirlite_ModuleTraverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GET_STATE(m)->HiErr_Base);
    return 0;
}

static int hirlite_ModuleClear(PyObject *m) {
    Py_CLEAR(GET_STATE(m)->HiErr_Base);
    return 0;
}

static struct PyModuleDef hirlite_ModuleDef = {
    PyModuleDef_HEAD_INIT,
    MOD_HIRLITE,
    NULL,
    sizeof(struct hirlite_ModuleState), /* m_size */
    NULL, /* m_methods */
    NULL, /* m_reload */
    hirlite_ModuleTraverse, /* m_traverse */
    hirlite_ModuleClear, /* m_clear */
    NULL /* m_free */
};
#else
struct hirlite_ModuleState state;
#endif

/* Keep pointer around for other classes to access the module state. */
PyObject *mod_hirlite;

#if IS_PY3K
PyMODINIT_FUNC PyInit_hirlite(void)
#else
PyMODINIT_FUNC inithirlite(void)
#endif

{
    if (PyType_Ready(&hirlite_RliteType) < 0) {
#if IS_PY3K
        return NULL;
#else
        return;
#endif
    }

#if IS_PY3K
    mod_hirlite = PyModule_Create(&hirlite_ModuleDef);
#else
    mod_hirlite = Py_InitModule(MOD_HIRLITE, NULL);
#endif

    /* Setup custom exceptions */
    HIRLITE_STATE->HiErr_Base =
        PyErr_NewException(MOD_HIRLITE ".HirliteError", PyExc_Exception, NULL);

    PyModule_AddObject(mod_hirlite, "HirliteError", HIRLITE_STATE->HiErr_Base);

    Py_INCREF(&hirlite_RliteType);
    PyModule_AddObject(mod_hirlite, "Rlite", (PyObject *)&hirlite_RliteType);


#if IS_PY3K
    return mod_hirlite;
#endif
}
