package main

/*
#include <stdlib.h>
#include <string.h>

typedef struct {
    const char* name;
    int age;
} MyGoStruct;
*/
import "C"
import "unsafe"

//export create_go_struct
func create_go_struct(name *C.char, age C.int) *C.MyGoStruct {
    // Calcule la taille de la chaîne
    size := C.strlen(name) + 1
    
    // Alloue de la mémoire pour la chaîne en C
    cname := C.malloc(size)
    // Copie la chaîne name dans cname
    C.memcpy(cname, unsafe.Pointer(name), size)
    
    // Alloue de la mémoire pour la structure
    s := (*C.MyGoStruct)(C.malloc(C.sizeof_MyGoStruct))
    s.name = (*C.char)(cname)
    s.age = age
    
    return s
}

//export free_go_struct
func free_go_struct(s *C.MyGoStruct) {
    if s != nil {
        if s.name != nil {
            C.free(unsafe.Pointer(s.name))
        }
        C.free(unsafe.Pointer(s))
    }
}

func main() {}
