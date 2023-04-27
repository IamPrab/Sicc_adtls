# Open a file in write mode with .jsl extension
file = open("example.jsl", "w")

# Write the code to the file
file.write("//!\nInclude(\".\\plotAxelLimitsFunction.jsl\" );\n\nplotLimits(\"Hello World\");")

# Close the file
file.close()
