#ifndef __HIRLITE_PY_H
#define __HIRLITE_PY_H

#include <Python.h>

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

#if PY_MAJOR_VERSION >= 3
#define IS_PY3K 1
#endif

#ifndef MOD_HIRLITE
#define MOD_HIRLITE "hirlite"
#endif

struct hirlite_ModuleState {
    PyObject *HiErr_Base;
};

#if IS_PY3K
#define GET_STATE(__s) ((struct hirlite_ModuleState*)PyModule_GetState(__s))
#else
extern struct hirlite_ModuleState state;
#define GET_STATE(__s) (&state)
#endif

/* Keep pointer around for other classes to access the module state. */
extern PyObject *mod_hirlite;
#define HIRLITE_STATE (GET_STATE(mod_hirlite))

#ifdef IS_PY3K
PyMODINIT_FUNC PyInit_hirlite(void);
#else
PyMODINIT_FUNC inithirlite(void);
#endif

#endif
