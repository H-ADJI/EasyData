# EasyData
A low code tool to easly collect data from any website using simple configuration.

## Documentation

### Scraping plans guide

Scraping plans are human-readable YAML templates that users can use to program web scraping / automation without advanced knowledge around the web scraping domain.

### Basics

A scraping plan is basically a listing of interactions that are needed to navigate and locate data in a website and then retrieve it in a flexible
format. Each interaction item defined in the interactions list is an object (json object for web gurus or a dictionary for fellow pythonistas) that
contains many fields.

Example of an interactions list :

```yaml
interactions:
    - object_that_define_interaction _1
    - object_that_define_interaction _2
    - object_that_define_interaction _3
    - ...
```

### Interaction objects

### Basic Browser Interactions

**do_once :**

it allows the user to perform an **action** on the browser (basically call a macro / function) once.
For each action (function), the user should provide the necessary inputs.

```yaml
interactions:
    - do_once: functionality_to_execute
      inputs:
        func_parameter_1: argument
        func_parameter_2: argument
        func_parameter_3: ...
    - ...
```

**inputs** are defined as an object that contains the parameters and their corresponding argument that will be fed to the function, that being said the
user should be aware of the required and optional input parameters of each function.
Refer to interaction functions documentation for more details.

### Repeated Browser Interactions

Usually when collecting data from a website, the need of a repeated execution of interactions arises (iterating over multiple pages, scrolling until
a condition is met...), and for this purpose two keywords allows this behavior : **do_until** and **do_many** allows the user to perform multiple
iterations over some actions (one or many actions) on the browser.
The user decides whether to loop over an array of elements (using the **for_each** keyword) or to iterate for a fixed number of times (using the **for**
keyword) or to keep the loop running until a condition is met.

**Known Number of iterations :**

The **do_many** keyword can be used with a fixed range of repetitions when used with the keyword for, the interactions defined inside the scope of do_many
will be repeated N times.

```yaml
interactions:
    - do_many: "placeholder_variable"
      for: N
      interactions:
        - object_that_define_interaction _1
        - object_that_define_interaction _2
        - object_that_define_interaction _3
        - ...
        - ...
```

The **do_many** keyword can also be used with an array of elements, the interactions defined inside the scope of do_many will be repeated for every element of
the array.


```ỳaml
interactions:
    - do_many: "placeholder_variable"
      for_each:
        - array_element_1
        - array_element_2
        - array_element_3
        - ...
      interactions:
        - object_that_define_interaction _1
        - object_that_define_interaction _2
        - object_that_define_interaction _3
        - ...
        - ...
```

## Architecture

### Functional components

The diagram below showcases the component that composes this tool

![architecture image](/assets/architec.png "architecture")

### Design of the scraping workflow templating and execution logic

### Database Design

### Scheduler Design

## Bugs problems and limitation
