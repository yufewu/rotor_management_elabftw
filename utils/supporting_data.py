STATUS_OPTIONS = ["Empty", "Borrowed", "Crashed/Broken/Missing", "Reference"]
HEADER = "Timestamp,Owner,Status,Sample name,Location,Note,Date"
END_TAG = "<p>---------------------------</p>"

HELP_ON_ROTOR_NUMBERS_TEXT = """
    **Help on rotor numbers:**
            
    The unique rotor number take the format of **YYXXX**
            
    **YY** - represents the size of the rotor, 07 for 0.7 mm, 13 for 1.3 mm, 31 for 3.2 mm thick wall, 
            32 for 3.2 mm thin wall, and 40 for 4.0 mm.
    
    **XXX** - represents the normal number of the rotor within its category. 
    """

UPDATING_INSTRUCTIONS_TEXT = """
    **Instructions:**
    1. Enter the number of the rotor you want to update in the text bar.
    2. The system will automatically retrieve the current status of the rotor from eLabFTW.
    3. Edit the information. The current information will be updated if the rotor already exists, or a new rotor will be created. 
    4. Click the "Submit" button when you are finished making changes. 
    5. All changes will be synchronized to eLabFTW at the same time.
    """

ROTOR_SIZES = ["07", "13", "31", "32", "40"]