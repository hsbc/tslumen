# Contributing

This page provides guidance and useful information about contributing to tslumen.


## Process

All contributions should be tied to a GitHub issue. An issue should be
filed under one of three categories:

- Bug report
- Documentation improvement
- Feature request

Details required for each category will be different; the issue template
should guide the user to through the process.

Once created, the issue will be given the `triage` label, regardless
of the category it belongs to. Once reviewed it will either be accepted
(thus dropping the `triage` label) or rejected. In case it is rejected,
the issue will be marked with the label `Won't fix` and closed.

Before proceeding to implement a feature or patch, we recommend to wait
for the issue to be approved and to get some feedback, namely on the
implementation strategy. Doing so should expedite the process and help
with keeping the code base consistent.

Similarly, the repository owners should offer guidance in setting the
target release version. It is important to do so ahead of any changes to
the code, so that the appropriate branch can be selected as the base, thus
reducing the likelihood of conflicts arising when attempting to merge.

Once there's an agreed upon implementation strategy and target release,
the development process can start. The first step should be to create a
branch off of the release branch. There are naming conventions that must
be followed, which can be found in the *Source control* section.

To get the changes merged a Pull Request needs to be raised, reviewed
and approved.  For better visibility and continuous involvement, the Pull
Request can be raised even before the changes are finalized, just make
sure to mark it as *draft*. Be sure to point to the correct target branch,
as by default GitHub assumes all Pull Requests are to go into `main`.

During the review process there might be questions or comments and
additional changes to the code as a result. Make sure to keep all the
changes in the same branch and inform the reviewers of the progress.

Once approved and merged to the release branch, your changes will be on
their way into the next release.



## Source management

### Ground rules

Git and GitHub are used for version control/source management of the
complete codebase of tslumen.

Some branches serve special purposes and are protected against direct
commits (except from administrators). These would include the `main` and
release branches, as well as the documentation branch `gh-pages`. Changes
to these branches should happen exclusively via Pull requests.

All development work -- be it bug fixes, new features or changes to
the documentation -- should be done off of feature branches, which need
to undergo a code review cycle supported on a Pull Request before being
merged to protected branches.


### Review process

All review comments should be recorded in GitHub next to the line/block
of code they refer to.  If the comment is more general and covers the
entire file, preferably stick it to the top.

The reviewer who raised the comment should be the one marking it as
resolved. To signal that the comment has been addressed, and the changes
implemented, the submitter should leave a reply in the appropriate
comment.

Make sure to reply to all comments that have been addressed, so that
the reviewer knows that particular issue ready for a subsequent review.

When in doubt or disagreement, use the review comments to engage in
discussion. This allows the community to chip in with their views and
forces everyone to articulate their thoughts in a well-structured manner.

Once the reviewer is happy with the changes, the Pull Request will be
marked as approved. Avoid pushing any more changes to the branch, or
you'll trigger a new review cycle.


### Important things to keep in mind

* Pull requests should have short and meaningful titles as well as a clear description of the changes
* Git client must be configured properly to prevent committing as an unrecognized author
* Secrets, local configs and dependencies should not leak into source control
* Binaries and data should not, in principle, be kept under source control (exceptions may apply)
* Commits should be clean, single-purposed and accompanied by a meaningful commit message
* Commit early; commit often
* Branches should be kept up to date and ideally be merged soon to prevent becoming stale
* Stale branches should be deleted, ideally by their owners



## Developing


### Environment setup

Make sure that your name and email are configured in your git client so
that your commits and Pull Requests are signed.

```bash
git config --global user.name "<Your Name>"
git config --global user.email <youremail@something.com>
```

To avoid dependency issues, the recommendation is to work off of a
sandboxed python environment. Assuming you have `virtualenv` installed:

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-extras.txt
pip install -r requirements-dev.txt
```

The first two requirements files contain the package dependencies --
core and extras, respectively. The dev one includes some additional
packages required only to support the development process (i.e. linters,
test frameworks, doc generation etc.)


### Coding standards

#### Why are they needed

* **Readability** – following a consistent convention makes it easier to read the code, as it prevents styling differences that can be distracting and encourages general good programming practices that make the logic easier to follow.
* **Consistency** – code should be considered a company asset and, as such, be cohesive rather than exhibit the individual preferences of each developer. 
* **Maintainability** – a consistent and easy to read codebase is easier to maintain.
* **Lower the TCO** – all previously mentioned aspects contribute in lowering the total cost of ownership. The induction of new contributors, as an example, should be much smoother when these standards are being followed.

#### Coding Standards in detail

**Idiomatic Python**
* Zen of Python – `import this`
>   The Zen of Python, by Tim Peters  
>      
>   Beautiful is better than ugly.  
>   Explicit is better than implicit.  
>   Simple is better than complex.  
>   Complex is better than complicated.  
>   Flat is better than nested.  
>   Sparse is better than dense.  
>   Readability counts.  
>   Special cases aren't special enough to break the rules.  
>   Although practicality beats purity.  
>   Errors should never pass silently.  
>   Unless explicitly silenced.  
>   In the face of ambiguity, refuse the temptation to guess.  
>   There should be one-- and preferably only one --obvious way to do it.  
>   Although that way may not be obvious at first unless you're Dutch.  
>   Now is better than never.  
>   Although never is often better than *right* now.  
>   If the implementation is hard to explain, it's a bad idea.  
>   If the implementation is easy to explain, it may be a good idea.  
>   Namespaces are one honking great idea -- let's do more of those!
* DRY (Don’t Repeat Yourself)
  * If you find you’re having to repeat the same logic (eventually with small variations) over and over, you are repeating yourself and contributing to an unnecessarily complex solution
  * Try to package blocks of logic into reusable representations
* Code should be modular and broken down in smaller functions
  * Avoid long functions with too many lines of code
  * Instead, try to have higher levels of abstraction
  * The logical stages within your function can be isolated into smaller functions, even if you won’t have to use them more than once, it makes the code easier to grasp
* Separation of concerns
  * When designing your program, make sure to break it enough so that there’s as little overlap in functionality as possible
* Don’t reinvent the wheel
  * First see if what you’re attempting to do already exists
  * If you require a slight variation on existing logic, think of the best options to extend it, rather than replicating blocks of code
  * If it’s available as an external library or there’s an industry standard way for doing it, favor adoption over adaptation
* Encapsulation: 
  * Consider variables and methods visibility – what is exposed is a de facto contract
  * Though Python is inherently open, there are conventions that help signaling to the consumers what is for public consumption and what should be seen as internal

**Code Layout** -- mostly enforced by `black`+`flake8`
* Indentation:
  * Spaces only! No tabs or mixed indentation
  * 4 spaces per indentation level
  * Continuation lines should be aligned vertically or with hanging indents
* Maximum Line Length: 99 characters
* Line Breaks: preferably break before each operator
* Blank Lines
  * 2 blank lines surrounding top-level function and class definitions
  * 1 blank line surrounding methods inside a class
  * 1 blank line in functions, sparingly, to indicate logical sections
* Imports:
  * Always at the top of the file
  * Grouped as follows: standard libraries, third-party libraries; local libraries
  * One import per line
  * Avoid wildcard imports
* Source File Encoding: utf-8, no need for encoding declaration

**Naming conventions**
* Use meaningful, descriptive names
* Methods and functions: verbs in present or infinitive
* Classes and variables: names
* Collections should be plural
* Single entities should be singular
* Avoid abbreviations
* Class names in CapWords
* Variable and functions in lowercase separated by underscores
* Constants in capital letters separated by underscores
* Private variables and methods should have a leading underscore

**Documentation**
* Docstrings present on all modules, classes and methods/functions
* All docstrings to be written in Google format
* When documenting a function, make sure each argument, the return value(s) and explicit exceptions are documented
* Comments should capture the functionality rather than describing what each line of code is doing
* Documentation should follow a top down approach, start by summarizing before diving into the nit-picky details
* When writing comments, think from the perspective of the reader and ensure the necessary context is provided as well as any useful details
* Where relevant include examples

**Warnings and Exception Handling**
* Warnings raised where relevant, but should be used sparingly
* Ensure proper exception handling is included
* Avoid using generic exceptions when possible

**Miscellaneous**
* Be careful with hardcoded values or configurations directly tied to your particular setup
* All code should include unit tests


### Unit tests guidelines

Writing unit tests clarifies thinking about the contracts of the code
they test, as well as the dependencies of that code.

Unit tests should:
* Run quickly – ideally the entire test suite should be executed before every code check in. Keeping the tests fast reduce the development turnaround time.
* Be straightforward to write
* Be independent – tests should avoid coupling with other tests, or with parts of the application which they are not responsible for testing.
* Be predictable
* Test only at unit level – avoid the temptation to test an entire work-flow using a unit testing framework, as it will make tests slow and hard to maintain.
* Check just one thing – when in testing mode it is sometimes tempting to assert on “everything” in every test; this should be avoided as it makes maintenance hard and the tests redundant
* Provide excellent coverage – the goal of a test suite should be to ensure high execution coverage by exploring as many code paths as possible
* Assist in case of failure – helping to diagnose and repair and to confirm missing or incomplete implementations

#### Unit tests conventions

* Unit tests should be organized to closely follow the source directory/package that they correspond to, making it easy to draw a parallel between implementation and test cases.
* Naming conventions:
  * Classes – prefix with `Test`, e.g. test class for FooBar should be named TestFooBar
  * Functions/methods – prefix with `test_`, e.g. test_barbarbar
  * Should be obvious from the name what is it that is being tested, e.g. test_div_zero suggests the aim of the test is to stress a division by zero.
* Ensure you are not relying on local configurations or setup nor are you connecting to predefined external resources
  * Unit tests should be written without explicit knowledge of the environment context in which they are executed so that they can be run anywhere at any time
  * In order to provide required resources for a test these resources should instead be made available by the test itself
  * Consider for instance a class for parsing files of a certain type. Instead of picking a sample file from a predefined location, put the file content inside the test, write it to a temporary file in the test setup process and delete the file when the test is done.
  * If this is not feasible, an alternative is to maintain a separate directory for resources required by the tests.
* Test both the trivial cases and the boundary cases
  * Make sure the parameter boundary cases are covered.
  * For numbers, test negatives, 0, positive, smallest, largest, NaN, infinity, etc.
  * For strings test empty string, single character string, non-ASCII string, multi-MB strings etc.
  * For dates, test January 1, February 29, December 31 etc.
  * The class being tested will suggest the boundary cases in each specific case. The point is to make sure as many as possible of these are tested properly as these cases are the prime candidates for errors.
* Include negative tests
  * Negative tests intentionally misuse the code and verify robustness and appropriate error handling.
* The code to be tested should not have any hidden inputs
  * An example would be a method that reads the current system time and returns a result based on that value.
  * Such non-deterministic behavior makes it impossible to test the internal logic of the method without actually changing the system date and time.
  * One workaround for this sort of situation is to create mock objects for the required dependencies.


### Makefile

Common build-related tasks can be performed with `make`. Main rules
included in the Makefile:
* `docs` -- shortcut to run the documentation's makefile; fully regenerates the documentation
* `tests` -- runs pytest with coverage and prints the coverage report
* `cq` -- shorthand for "code quality", runs black, flake8 and mypy (styling, linting and type checking)
* `build` -- installs the requirements, builds a wheel and source dist and checks with twine
* `all` -- does the whole lot (except the documentation)
