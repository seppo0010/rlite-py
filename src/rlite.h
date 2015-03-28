#ifndef __RLITE_H
#define __RLITE_H

#include "hirlite.h"
#include <rlite/hirlite.h>

typedef struct {
    PyObject_HEAD
    rliteContext *context;
    char *encoding;
    PyObject *replyErrorClass;
} hirlite_RliteObject;

extern PyTypeObject hirlite_RliteType;

#endif
