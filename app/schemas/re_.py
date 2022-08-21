USERNAME_REGEX = r'^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$'
"""
https://stackoverflow.com/a/12019115/17221540

(?=.{5,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9_]+(?<![_.])$
└─────┬────┘└───┬──┘└─────┬─────┘└─────┬─────┘ └───┬───┘
   │         │         │            │           no _ or . at the end
   │         │         │            │
   │         │         │            allowed characters
   │         │         │
   │         │         no __ or _. or ._ or .. inside
   │         │
   │         no _ or . at the beginning
   │
   username is 5-20 characters long
"""
