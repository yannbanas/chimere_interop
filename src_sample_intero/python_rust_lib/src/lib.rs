// src/main.rs
#[repr(C)]
pub struct MyRustStruct {
    name: *const std::os::raw::c_char,
    age: i32,
}

#[no_mangle]
pub extern "C" fn create_rust_struct(name: *const std::os::raw::c_char, age: i32) -> *mut MyRustStruct {
    use std::ffi::CStr;
    let c_str = unsafe { CStr::from_ptr(name) };
    let s = MyRustStruct {
        name: c_str.as_ptr(),
        age: age,
    };
    let boxed = Box::new(s);
    Box::into_raw(boxed)
}

#[no_mangle]
pub extern "C" fn free_rust_struct(ptr: *mut MyRustStruct) {
    if !ptr.is_null() {
        unsafe {
            Box::from_raw(ptr); // Box sera drop ici
        }
    }
}

