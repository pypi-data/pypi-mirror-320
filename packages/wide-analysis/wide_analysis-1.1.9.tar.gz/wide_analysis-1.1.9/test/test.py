"""
This is a test file

"""

from wide_analysis import analyze

url = 'https://el.wikipedia.org/wiki/Βικιπαίδεια:Σελίδες_για_διαγραφή/Δεκεμβρίου_2024#Κατάλογος_αλυσίδων_του_λιανεμπορίου_στην_Ελλάδα'
task = "outcome" 

try:
    result = analyze(inp=url, 
                    mode ='title',
                    task='outcome', 
                    openai_access_token='', 
                    explanation=False, 
                    lang='gr',
                    platform='wikipedia',
    ) #years='12/2024')


    print("Analysis successful!")
    print(result)
except Exception as e:
    print(f"Error during analysis: {e}")

