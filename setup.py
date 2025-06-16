'''
The setup.py file is an esssentil part of packaging and distributing python projects.
 it is used by setuptools ( or disutils in older python versions) to define the 
 configuration of your project, such as its metadata, dependencies and more
'''

from setuptools import find_packages, setup 
from typing import List 

def get_requirements()-> List[str]:
    """
    This function will return list of requirements
    Returns:
        List[str]: _description_
    """

    requirement_lst:List[str]=[] #here is how we can declare the variable with its datatype in python
    try:
        with open("requirements.txt", 'r') as f:
            #Read lines from the file
            lines=f.readlines()

            ##process each line
            for line in lines:
                requirement = line.strip()
                
                #ignore empty lines and -e .

                # here when we give this -e . in the requirements.txt, when we install the packages with pip install -r requirments.txt\
                # It will trigger the package creation with by running this setup.py also along with it. Else we may need to run setup.py seperately

                if requirement and requirement!='-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirement.txt file not found")

    return requirement_lst

#here our own python package will be created with the given credentials, and also it will 
# automatically take the entire project structure that we have created.
setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Rohan-Thoma",
    author_email='rohanvailalathoma@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements()
)



if __name__=="__main__":
    print(get_requirements())