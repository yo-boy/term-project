from prompt_toolkit import PromptSession
# Create prompt object.
session = PromptSession()


import mysql.connector
#setup local mysql database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123"
)

mycursor = mydb.cursor(dictionary=True)
def createDatabase():
# reset database
    mycursor.execute("DROP DATABASE IF EXISTS Twitch")
    mycursor.execute("CREATE DATABASE Twitch")
    mycursor.execute("USE Twitch")
    # create tables
    mycursor.execute("CREATE TABLE Twitch.Account (Name varchar(100) NOT NULL, `Email` varchar(100) NOT NULL, Balance FLOAT DEFAULT 0 NOT NULL, CONSTRAINT Account_PK PRIMARY KEY (Name))")
    mycursor.execute("CREATE TABLE Twitch.Stream (StreamID BIGINT auto_increment NOT NULL, AName varchar(100) NOT NULL, `Length` TIME NOT NULL, Viewers BIGINT DEFAULT 0 NOT NULL, Category varchar(100) NOT NULL, CONSTRAINT Stream_PK PRIMARY KEY (StreamID), CONSTRAINT Stream_FK FOREIGN KEY (AName) REFERENCES Twitch.Account(Name) ON UPDATE CASCADE)")
    mycursor.execute("CREATE TABLE Twitch.Follow ( Follower varchar(100) NOT NULL, Reciever varchar(100) NOT NULL, CONSTRAINT Follow_PK PRIMARY KEY (Follower,Reciever), CONSTRAINT Follow_FK FOREIGN KEY (Follower) REFERENCES Twitch.Account(Name) ON DELETE CASCADE ON UPDATE CASCADE, CONSTRAINT Follow_FK_1 FOREIGN KEY (Reciever) REFERENCES Twitch.Account(Name) ON DELETE CASCADE ON UPDATE CASCADE)")
    mycursor.execute("CREATE TABLE Twitch.Donation ( DonationID BIGINT auto_increment NOT NULL, Donator varchar(100) NOT NULL, Reciever varchar(100) NOT NULL, Amount FLOAT DEFAULT 0 NOT NULL, `Date` DATETIME NOT NULL, CONSTRAINT Donation_PK PRIMARY KEY (DonationID), CONSTRAINT Donation_FK FOREIGN KEY (Donator) REFERENCES Twitch.Account(Name) ON UPDATE CASCADE, CONSTRAINT Donation_FK_1 FOREIGN KEY (Reciever) REFERENCES Twitch.Account(Name) ON UPDATE CASCADE)")
    mycursor.execute("CREATE TABLE Twitch.Watch ( AName varchar(100) NOT NULL, StreamID BIGINT NOT NULL, CONSTRAINT Watch_PK PRIMARY KEY (AName,StreamID), CONSTRAINT Watch_FK FOREIGN KEY (AName) REFERENCES Twitch.Account(Name) ON DELETE CASCADE ON UPDATE CASCADE, CONSTRAINT Watch_FK_1 FOREIGN KEY (StreamID) REFERENCES Twitch.Stream(StreamID) ON DELETE CASCADE ON UPDATE CASCADE)")
    mycursor.execute("CREATE TABLE Twitch.Chat ( MID BIGINT auto_increment NOT NULL, AName varchar(100) NOT NULL, StreamID BIGINT NOT NULL, Message VARCHAR(100) NOT NULL, CONSTRAINT Chat_PK PRIMARY KEY (MID), CONSTRAINT Chat_FK FOREIGN KEY (AName) REFERENCES Twitch.Account(Name), CONSTRAINT Chat_FK_1 FOREIGN KEY (StreamID) REFERENCES Twitch.Stream(StreamID) ON DELETE CASCADE ON UPDATE CASCADE)")

createDatabase()

def chooseTable():
    i = 0
    mycursor.execute("SHOW TABLES;")
    tables = mycursor.fetchall()
    for table in tables:
        i += 1
        print(str(i)+ ": " +table['Tables_in_Twitch'])
    i += 1
    print(str(i)+ ": exit")
    choice = session.prompt("choose table: ")
    if choice == str(i):
        exit()
    return tables[int(choice)-1]['Tables_in_Twitch']

def showRecords():
    table = chooseTable()
    print("Records of " + table+ ":\n")
    mycursor.execute("SELECT * FROM "+ table + ";")
    for record in mycursor:
        for item in record:
            print(item + ": " + str(record[item]))
        print()

def addRecord():
    table = chooseTable()
    mycursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"+ table + "' ORDER BY ORDINAL_POSITION")
    string = "INSERT INTO " + table + " ("
    columns = []
    for column in mycursor:
        columns.append(column['COLUMN_NAME'])
        string += column['COLUMN_NAME'] + ", "
    string = string[:-2]
    string += ") VALUES ("
    tttt = "%s, " * len(columns)
    tttt = tttt[:-2]
    string += tttt + ");"
    data = []
    for column in columns:
        data.append(session.prompt("enter " + column + ": "))
    print(string)
    mycursor.execute(string, data)
    mycursor.execute("select * from "+ table+ ";")
    print(mycursor.fetchall())

    
def showMenu():
    print("1: list records\n2: add records\n")
    choice = session.prompt("enter choice: ")
    match choice:
       case "1":
            showRecords()
       case "2":
            addRecord()

showMenu()
