'''
Created on Aug 12, 2025

@author: matze
'''

'''
#Kurs;Aktivität;Raum;Wochentag;Von;Bis;
Faszien;GroupFitnesse;Spiegelsaal;Mo;9:00;10:00;
'''

import csv


class CSVReader():
    HEADER="headers"
    ENTRIES="data"
    
    def __init__(self):
        self.entries = [];
        self.header=[]
    
    def read(self,pathName,hasTrailingDelimiter=True,code='utf-8',delim=';'):
        with open(pathName,"r", encoding=code) as csvfile:
        #with open(pathName,"r",newline="") as csvfile:            
            reader = csv.reader(csvfile, delimiter=delim)
            isHeader=True
            for row in reader:
                rowLen = len(row)-1 if hasTrailingDelimiter else len(row) 
                if len(row[0])>1 and row[0][1] != '#':
                    if isHeader:
                        self.header.append(row[:rowLen])
                        isHeader=False
                    else:
                        self.entries.append(row[:rowLen])
        return self.entries

    def filter(self,indexArray):
        dic={}
        dic[CSVReader.HEADER] = [line[i] for i in indexArray for line in self.header]
        if len(indexArray)==1:
            dic[CSVReader.ENTRIES] = [line[i] for i in indexArray for line in self.entries]
        else:
            dic[CSVReader.ENTRIES] = [[line[i] for i in indexArray] for line in self.entries]
        return dic
                  


def mailCSVKasData():
    cr = CSVReader();
    filepath = "/home/matze/Documents/Shared/KAS-MAIL/Mailaccounts(KAS).csv"
    cr.read(filepath,False,'utf-8-sig') #to prevent leading BOOM
    #fields ="login;adresses;copy_adress;responder;password;is_active;used_mailaccount_space;Status;Migrationszeitraum;SharedMailbox".split(';') #ingore 1
    data = cr.filter([1,2,4,7,8,9])
    print("######### KAS SERVER %d count ##############"%(len(data[cr.ENTRIES])))
    print(data[cr.HEADER])
    for row in data[cr.ENTRIES]:
        print(row)
    return data
    
    
def mailCSVExchangeData():
    cr = CSVReader();
    filepath = "/home/matze/Documents/Shared/KAS-MAIL/MailboxesExchange.csv"
    cr.read(filepath,False,'utf-8-sig',',') #to prevent leading BOOM
    #fields ="Display name,Email address,Recipient type,Archive status,Last modified time".split(',') #1 & 2 only needed
    data = cr.filter([1])
    print("######### EXCHANGE SERVER %d count ##############"%(len(data)))
    print(data[cr.HEADER])
    #for row in data[cr.ENTRIES]:
    #    print(row)
    return data

#list of temporary users to be created BEFORE doing migration - and to be removed after those have been migrated and designated as shared accounts
def createdMailAccounts():
    kas = mailCSVKasData()
    ex = mailCSVExchangeData()
    kasData = kas[CSVReader.ENTRIES]
    exData = ex[CSVReader.ENTRIES]
    exLower = [row.lower()for row in exData]
    print(exLower)
    [0,3]
    tbd = [row[0] for row in kasData if row[0].lower() not in exLower and 'aktiv/migrieren' in row[3]]
    cnt =1
    for entries in tbd:
        print("%d) %s"%(cnt,entries))
        cnt +=1

def _rawMigrationBatch():
    kas = mailCSVKasData()
    kasData = kas[CSVReader.ENTRIES]
    #EmailAddress,UserName,Password -we need the new csv...
    blacklist=['it@tsv-weilheim.com','mathias.wegmann@tsv-weilheim.com','extest@tsv-weilheim.com','dieter.pausch@tsv-weilheim.com', 'erhard.fernholz@tsv-weilheim.com','spendengala@tsv-weilheim.com','anmeldung@tsv-weilheim.com','yvonne.laschewski@tsv-weilheim.com','jugendleitung.aikido@tsv-weilheim.com','stephanie.wagner@tsv-weilheim.com','extest@tsv-weilheim.com']
    data=[]
    for row in kasData:
        if 'aktiv/migrieren' in row[3] and row[0] not in blacklist:
            if len(row[2])<8:
                row[2]="TSV1847#EVALL"
            data.append(row)
    return data

#just the mirgation list for one year- EmailAddress,UserName,Password (username & mail adress are the same)
#status: aktiv/migrieren, Migrationszeitraum: 1Jahr
#blacklist: dieter.pausch@tsv-weilheim.com, erhard.fernholz@tsv-weilheim.com,spendengala@tsv-weilheim.com,anmeldung@tsv-weilheim.com
def createMigration1(rawData):
    data = []
    print("######## 1 year list ##############")
    print("EmailAddress,UserName,Password") 
    for row in rawData:
        if '1Jahr' in row[4]:
            print("%s,%s,%s"%(row[0],row[0],row[2]))
            data.append(row)
    print("--- %d entires --- "%(len(data)))
    
def anschreiben(rawData):

    data=[]
    for row in rawData:
            data.append(row[0])
            
    print("######## anschreiben #### %s ##########"%(len(data)))            
    print(','.join(data))
    

def verifyPasswords(rawData):
    print("######## Invalid passwords ##############")
    for row in rawData:
        if 'TSV1847#EVALL' in row[2]:
            print(row)        

#2 year recovery - else same but Migrationszeitraum: 2Jahre
def createMigration2(rawData):
    data = []
    print("######## 2 year list ##############")
    print("EmailAddress,UserName,Password") 
    for row in rawData:
        if '2Jahr' in row[4]:
            print("%s,%s,%s"%(row[0],row[0],row[2]))
            data.append(row)
    
    print("--- %d entries --- "%(len(data)))
    
def listSharedBoxes(rawData):
    data = []
    print("######## shared list (only for reference!) ##############")
    for row in rawData:
        if 'WAHR' in row[5]:
            print("%s,%s,%s"%(row[0],row[0],row[2]))
            data.append(row)
    
    print("--- %d entries --- "%(len(data)))
    
def listForwards(rawData):
    print("######## Forwarding ##############")
    for row in rawData:
        if row[1]:
            print("%s -> %s"%(row[0],row[1]))
    
def makeContactLists():
    blacklist=['jugendleitung.aikido@tsv-weilheim.com','stephanie.wagner@tsv-weilheim.com','extest@tsv-weilheim.com','dieter.pausch@tsv-weilheim.com', 'erhard.fernholz@tsv-weilheim.com','spendengala@tsv-weilheim.com','anmeldung@tsv-weilheim.com','yvonne.laschewski@tsv-weilheim.com']
    cr = CSVReader();
    filepath = "/home/matze/Documents/Shared/KAS-MAIL/w00d4ed3-mailforwards-Manuel.csv"
    cr.read(filepath,False,'utf-8-sig',',') #to prevent leading BOOM
    #fields ="Display name,Email address,Recipient type,Archive status,Last modified time".split(',') #1 & 2 only needed
    #print(cr.entries)
    print("GroupName","GroupEmail","MemberType","MemberName","MemberEmail")
    for row in cr.entries:
        count=0
        group,_=row[0].split('@')
        for user in row[1:]:
            if user and user not in blacklist:
                name,domain = user.split('@')
                if "sv-weilheim.com" in domain:
                    mtype = "User" 
                else:
                    mtype="Contact"
                
                count+=1
                print("%s,%s,%s,%s,%s"%(group,row[0],mtype,name,user))
                
        print("######### %s has %d members #########"%(group,count))
        

if __name__ == '__main__':
    rawData = _rawMigrationBatch()
    
    #createMigration1(rawData)
    #createMigration2(rawData)
    #listSharedBoxes(rawData)
    listForwards(rawData)
    #verifyPasswords(rawData)
    #makeContactLists()
    #anschreiben(rawData)