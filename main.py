from prompt_toolkit import PromptSession
# Create prompt session object, this allows the user to have a history when inputting
# things in the prompt
session = PromptSession()

import mysql.connector
#setup local mysql database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123"
)
#using the dictionary option makes it simpler to do some things with SQL
mycursor = mydb.cursor(dictionary=True)
def createDatabase():
    # reset database
    mycursor.execute("DROP DATABASE IF EXISTS Twitch")
    mycursor.execute("CREATE DATABASE Twitch")
    mycursor.execute("USE Twitch")
    # create tables
    mycursor.execute("CREATE TABLE Twitch.Account (Name varchar(100) NOT NULL, `Email` varchar(100) NOT NULL, Balance FLOAT DEFAULT 0 NOT NULL, CONSTRAINT Account_PK PRIMARY KEY (Name))")
    # note that we specify what happens when we update or delete records in the Account table, this is to make sure we don't leave hanging records that point to accounts that don't exist
    mycursor.execute("CREATE TABLE Twitch.Stream (StreamID BIGINT auto_increment NOT NULL, AName varchar(100) NOT NULL, `Length` TIME NOT NULL, Viewers BIGINT DEFAULT 0 NOT NULL, Category varchar(100) NOT NULL, CONSTRAINT Stream_PK PRIMARY KEY (StreamID), CONSTRAINT Stream_FK FOREIGN KEY (AName) REFERENCES Twitch.Account(Name) ON UPDATE CASCADE)")
    mycursor.execute("CREATE TABLE Twitch.Follow ( Follower varchar(100) NOT NULL, Reciever varchar(100) NOT NULL, CONSTRAINT Follow_PK PRIMARY KEY (Follower,Reciever), CONSTRAINT Follow_FK FOREIGN KEY (Follower) REFERENCES Twitch.Account(Name) ON DELETE CASCADE ON UPDATE CASCADE, CONSTRAINT Follow_FK_1 FOREIGN KEY (Reciever) REFERENCES Twitch.Account(Name) ON DELETE CASCADE ON UPDATE CASCADE)")
    mycursor.execute("CREATE TABLE Twitch.Donation ( DonationID BIGINT auto_increment NOT NULL, Donator varchar(100) NOT NULL, Reciever varchar(100) NOT NULL, Amount FLOAT DEFAULT 0 NOT NULL, `Date` DATETIME NOT NULL, CONSTRAINT Donation_PK PRIMARY KEY (DonationID), CONSTRAINT Donation_FK FOREIGN KEY (Donator) REFERENCES Twitch.Account(Name) ON UPDATE CASCADE, CONSTRAINT Donation_FK_1 FOREIGN KEY (Reciever) REFERENCES Twitch.Account(Name) ON UPDATE CASCADE)")
    mycursor.execute("CREATE TABLE Twitch.Watch ( AName varchar(100) NOT NULL, StreamID BIGINT NOT NULL, CONSTRAINT Watch_PK PRIMARY KEY (AName,StreamID), CONSTRAINT Watch_FK FOREIGN KEY (AName) REFERENCES Twitch.Account(Name) ON DELETE CASCADE ON UPDATE CASCADE, CONSTRAINT Watch_FK_1 FOREIGN KEY (StreamID) REFERENCES Twitch.Stream(StreamID) ON DELETE CASCADE ON UPDATE CASCADE)")
    mycursor.execute("CREATE TABLE Twitch.Chat ( MID BIGINT auto_increment NOT NULL, AName varchar(100) NOT NULL, StreamID BIGINT NOT NULL, Message VARCHAR(100) NOT NULL, CONSTRAINT Chat_PK PRIMARY KEY (MID), CONSTRAINT Chat_FK FOREIGN KEY (AName) REFERENCES Twitch.Account(Name), CONSTRAINT Chat_FK_1 FOREIGN KEY (StreamID) REFERENCES Twitch.Stream(StreamID) ON DELETE CASCADE ON UPDATE CASCADE)")

# asks the user to choose one of the tables after listing them
def chooseTable():
    print()
    i = 0
    mycursor.execute("SHOW TABLES;")
    tables = mycursor.fetchall()
    for table in tables:
        i += 1
        print(str(i)+ ": " +table['Tables_in_Twitch'])
    choice = session.prompt("\nchoose table: ")
    return tables[int(choice)-1]['Tables_in_Twitch']

# shows the records of a table after asking the user to choose a table
def showRecords():
    table = chooseTable()
    print("Records of " + table+ ":\n")
    mycursor.execute("SELECT * FROM "+ table + ";")
    contents = mycursor.fetchall()
    if contents == []:
        print("table is empty")
    for record in contents:
        for item in record:
            print(item + ": " + str(record[item]))
        print()

# asks user to choose a table then adds a record to it, it asks the user to input a value for each column of the table
def addRecord():
    table = chooseTable()
    # with this statement we get all of the columns names for a table
    mycursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"+ table + "' ORDER BY ORDINAL_POSITION")
    # we start constructing the main statement string 
    string = "INSERT INTO " + table + " ("
    columns = []
    # we collect the columns in an array
    for column in mycursor:
        columns.append(column['COLUMN_NAME'])
        string += column['COLUMN_NAME'] + ", "
    string = string[:-2] # removing the extra space and comma in the string
    string += ") VALUES ("
    temp = "%s, " * len(columns) # making a string with %s so we can input the values
    temp = temp[:-2] # removing the extra comma and space
    string += temp + ");" # finishing the string
    data = [] # asking the user for data
    for column in columns:
        data.append(session.prompt("enter " + column + ": "))
    mycursor.execute(string, data) # executing the finished statement

# deletes a record after first asking the user to choose a table then asking them to choose a record
def deleteRecord():
    table = chooseTable()
    print("choose record to delete:\n")
    mycursor.execute("SELECT * FROM "+ table + ";")
    i = 1
    tempRecordArray = []
    for record in mycursor:
        tempRecordArray.append(record)
        print(str(i) + ":")
        i += 1
        for item in record:
            print(item + ": " + str(record[item]))
        print()
    choice = session.prompt("choose record to delete: ")
    temp = tempRecordArray[int(choice)-1]
    # this statement takes the first key from the dictionary, which will be the primary key
    # because the primary key is first in all our tables
    columnToDelete = next(iter(temp)) 
    # we put the value we want to delete in a list because the cursor.execute multivalue mode only takes a list and not a single value
    valueToDelete = []
    valueToDelete.append(tempRecordArray[int(choice)-1][columnToDelete])
    statement = "DELETE FROM " + table + " WHERE " + columnToDelete + "= %s;"
    mycursor.execute(statement,valueToDelete)

# this function allows the user to execute any SQL statement they want and outputs the results if there are any.
def executeSQL():
    statement = session.prompt("enter SQL statement to execute on database: ")
    mycursor.execute(statement)
    print(mycursor.fetchall())

# shows a menu and allows the user to choose between operations to apply to the database or exit the program
def showMenu():
    print("\nChoose operation: ")
    print("\n1: list records\n2: add a record\n3: delete a record\n4: execute SQL statement\n5: reset database\n6: exit\n")
    choice = session.prompt("enter choice: ")
    match choice:
        case "1":
            showRecords()
        case "2":
            addRecord()
        case "3":
            deleteRecord()
        case "4":
            executeSQL()
        case "5":
            createDatabase()
        case "6":
            exit()

# creates a fresh database and starts the menu
def main():
    createDatabase()
    while True:
        showMenu()

main()
