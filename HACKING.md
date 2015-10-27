# Workflow

To contribute code/edit/etc:

1. [Install git](http://git-scm.com/book/en/Getting-Started-Installing-Git) (if
   you haven't already)

2. Make a github account

3. Clone the repo:

        $ git clone https://github.com/voicesauce/opensauce-python.git
        $ cd opensauce-python

4. To run the existing unit tests:

        $ python -m unittest test

5. Write code, edit code, test code.  Ideally, add tests to the set of
   unit tests in the tests directory to cover any new or changed code.
   New tests will be automatically picked up by the test runner if
   (a) any test class subclasses unittest.TestCase and (b) any
   test method name starts with the string 'test_'.

6. To track added or changed files, use "git add":

        $ git add path/to/file

7. Once you're ready to commit your changes, use "git commit":

        $ git commit

   An editing window will open for the commit message.  Please start it with a
   one line summary of the change, a blank line, and then a paragraph or two
   about the motivation for the change and what the changes are.

8. Push your changes to the cloud (it'll ask for your github username and
   password):

        $ git push


In order to sync your version of the repo with the master copy, use "git pull":

        $ git pull

If something breaks or anything is confusing, e-mail me: ksilvers at umass dot
edu


# Projects

Check the Issue tracker and TODO.md for ideas.
