# Python’s "pass-by-object-reference" paradigm when passing variables into functions

When you pass an immutable object (string, boolean, number, tuple) to a function in Python, you are actually passing a *reference* (alias) to that object, not a copy of it (pass by value). And as long as you do not attempt to modify that object within the function, the reference points to the original object, and no new object is created. Therefore, you are actually "dealing with" (accessing) the original object in memory through its reference.

However, if you attempt to **modify** an *immutable* object within a function, what actually happens is a bit different from mutable objects. Modifying a *mutable* object does not create a new copy; rather, it just modifies the original object's value in memory (in-place).

But since immutable objects cannot be changed in memory after they are created, any operation that seems to "modify" the object will actually **create** a new distinct object (copy) in memory. Python then re-binds the local variable name to that new object within the function's scope. The original object passed into the function remains unchanged because it was never modified; instead, a new object was created out of it and referenced by the local variable in the function.

## Summary

Reference (Python sense): is a variable name (alias) bound to an object. Multiple aliases can refer to the same object. *Assignment never copies* the object; it re-binds a name.

Pointer (C/C++ sense): a memory address that you can: manipulate arithmetically, dereference explicitly, etc. Python does not expose that model directly (though tensors have underlying storage pointers you can inspect with `data_ptr()`, but you do not program with them like C pointers).

_Note_: A **pointer** is an *independent* variable (has its own memory address) that stores the memory address of another variable, whereas a **reference** is an alias (an alternative name) for an already existing variable and shares its exact same memory. A reference is like an automatically _dereferenced pointer_; directly accesses the data stored in that memory address.
