# EasyData

A low code tool using a DSL (Domaine Specific Language) to easly collect data from any website using simple configuration.

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

```yaml
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

In the two examples above the do_many value is set to a variable, this variable will hold the value of each iteration (either an element of the
array or the iteration number), this value then can be used as a variable inside the interactions list, as an input for an action or to be yielded with
the output data.

**Unknown Number of iterations :**

**do_until** allows the user to perform repeated iterations of a set of interactions until a condition is met.

Using the **do_until** keyword requires a **condition** field where all the required loop parameters are defined.

The **condition** field is an object that contains other fields defining all necessary data for the loop :

- **elements_selector** : (required) : An XPATH / CSS selector that refer to the element that should verify the condition defined above.
- **value** : the value to look for in a selected element before ending the loop.

The keyword do_until have 3 possible values :

- **match_value** : where the loop runs until the selected element* matches a certain value.
- **count** : where the loop runs until the count of the selected elements matches a certain value.
- **no_more** : where the loop runs until the count of the selected elements doesn't change between 2 iterations of the loop.

Usage of **do_until** with **match_value**. In this case the Condition object should contain a value field defining what value to look for.

```yaml
interactions:
  - do_until: "match_value"
    condition:
      elements_selector: XPATH OR CSS SELECTOR
      value: VALUE TO LOOK FOR IN THE SELECTED ELEMENT
    interactions:
      - object_that_define_interaction _1
      - object_that_define_interaction _2
      - object_that_define_interaction _3
      - ...
      - ...
```

Usage of **do_until** with **count**. In this case the Condition object should contain a value field defining the limit count of elements.

```yaml
interactions:
  - do_until: "count"
    condition:
      elements_selector: XPATH OR CSS SELECTOR
      value: COUNT OF THE SELECTED ELEMENTS TO END THE LOOP
    interactions:
      - object_that_define_interaction _1
      - object_that_define_interaction _2
      - object_that_define_interaction _3
      - ...
      - ...
```

Usage of **do_until** with **no_more**. In this case the Condition should only contain the selector for the elements to survey.

```yaml
interactions:
  - do_until: ""no_more""
    condition:
      elements_selector: XPATH OR CSS SELECTOR
    interactions:
      - object_that_define_interaction _1
      - object_that_define_interaction _2
      - object_that_define_interaction _3
      - ...
      - ...
```

### Interaction functions

Interaction functions define different actions that can be used to interact with a web page.

Below is a list of the supported functions that can be used within scraping plans

- visit_page : navigate to a url
  - inputs :
    - url : str = targeted url.

**Example :**

```yaml
interactions:
  - do_once: visit_page
      description: visiting the home page for hespress
      inputs:
        url: "https://www.hespress.com/"
```

- click : Click the element(s) matching the selector(s).
  - inputs :
    - selectors : List[str] = XPATH / CSS selector.
    - count (int, optional): number of click to execute. Defaults to 1.

**Example :**

```yaml
interactions:
  - do_once: click
    description: Clicking on the category button
    inputs:
      selectors:
        - //a[@class='nav-link' and text()="category"]
```

- use_keyboard : Send keystrokes to the element(s) matching the selector(s)
  - inputs :
    - keys : List[str] = keyboard keys to use (keys list reference)
    - selectors : (List[str],optional) = XPATH / CSS selector.

**Example :**

```yaml
interactions:
  - do_once: use_keyboard
    inputs:
      keys:
       - PageDown
```

- wait_for : wait until a change (either events or state changes not both) happens on a page or an locator element then returns.
  - inputs :
    - event : (Literal[load | domcontentloaded | networkidle]): event to watch for before returning.
    - state (Literal[attached | detached | visible | hidden]): the state of the element to wait for before returning. Defaults to None.
    - duration : int = explicitly waiting for an exact duration.
    - selectors List[str]: used to watch for a sub element instead. Required if we waiting for a state change for an element.

**Example :**

```yaml
interactions:
  - do_once: wait_for
    inputs:
      selectors:
        - //div[@class="spinner-border"]
      state: detached
```

- visit_page : navigate to a url
  - inputs :
  - url : str = targeted url.

**Example :**

```yaml
interactions:
  - do_once: visit_page
      description: visiting the home page for hespress
      inputs:
        url: "https://www.hespress.com/"
```

- scrape_page : extract data from a web page
  - inputs :
    - data_to_get : List[dict] = list of dictionaries each with contains a parameters that describe some data on the page**
    - selectors : List[str] = used to select the element containing the data we are interested in extracting.
    - include_order : (bool, optional) = whether to include in the output the order the extracted elements had on the web page. Defaults to False.
  
\*\***data_to_get** : this is an object (dictionary) describing where and in what format to retrieve the data from the page. the field that should be defined in data_to_get :

- **data_to_get** :
  - field_alias : str = the ouput data value will be assigned to this key
  - kind : Literal[ text | attribute | nested | generated ] = indicate whether the data to be extracted is contained in an element text or attribute
  - name : str = indicate the name of the attribute that contains the data. ( required if kind==attribute)
  - find_all : (bool,optional) = whether to extract all matching elements (True) or just the first matching element (False), Defaults to False.
  - relocate : List[str] = Selector used to relocate into another sub-element inside the element selected.
  - iframe : str = Selector used with relocate when the desired data is located inside an iframe.
  - processing**** : List[dict] = a list of processing function to be applied on the extracted data.

**Example :**

```yaml
interactions:
  - do_once: scrape_page
    inputs:
      selectors:
        - //div[@class='cover']
      data_to_get:
        - field_alias: title
          kind: attribute
          relocate:
            - //a
          name:
            - title
        - field_alias: image
          kind: attribute
          relocate:
            - //a//img
          name:
            - src
        - field_alias: date
          kind: text
          relocate:
            - //div[@class='card-body']//small
        - field_alias: url
          kind: attribute
          relocate:
            - //a
          name:
            - href
          processing:
            - function: decode_url
        - field_alias: category
          kind: text
          relocate:
            - //span[@class[contains( ., 'cat')]]
```

- block_routes : used to block url routes that interfere when loading a page. this will be mainly used to reduce loading ressource consumption by blocking unwanted ressources or to block ads.
  - inputs :
    - url_patterns : List[str] = url patterns to block when loading a web page, can be in a regex format or just plain url string.

**Example :**

```yaml
interactions:
  - do_once: block_routes
    description: block some uneeded request routes, will block ads from intervening and allow better performance with less requests
    inputs:
      url_patterns:
        - (?<!uplo)ads
```

## Data processing functions

Below is a list of supported **processing** functions :

- processing :
  - join_text
  - remove_punctuation
  - to_number
  - strip_whitespaces
  - arabic_datetime
  - remove_chars
  - remove_arabic_noise
  - normalize_arabic_letters
  - remove_repeated_letters
  - remove_stop_words

## Architecture

### Functional components

The diagram below showcases the component that composes this tool

![Use Dark Mode or it wont show up](/assets/architec.png#gh-dark-mode-only "architecture")

### Database Design

TODO

### Scheduler Design

TODO

### Design of the scraping workflow templating and execution logic

TODO

### Limitations and possible improvements

TODO
