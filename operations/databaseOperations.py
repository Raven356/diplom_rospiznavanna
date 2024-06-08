import pyodbc
from datetime import date, datetime
import hashlib
import uuid

class DatabaseOperations:
    server = '.'
    database = 'ObjectDetection'
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

    def insertNewAccident(self, location, classification, image_bytes, confidence):
        conn = pyodbc.connect(self.conn_str)

        cursor = conn.cursor()

        cursor.execute("Select Id from locations where Location = ?", (location))
        location_id = cursor.fetchone()[0]

        cursor.execute("Select Id from Classifications where Name = ?", (classification))
        classification_id = cursor.fetchone()[0]

        current_date = date.today().strftime('%Y-%m-%d')

        cursor.execute("INSERT INTO Accidents (LocationId, ClassificationId, Incident, Confidence, isFalsePositive, Date) VALUES (?, ?, ?, ?, ?, ?)",
                                   (location_id, classification_id, image_bytes.tobytes(), float(confidence), 0, current_date))
        conn.commit()
        conn.close()

    def getAccidentsForLocation(self, location, startDate, endDate):
        conn = pyodbc.connect(self.conn_str)

        cursor = conn.cursor()

        query, dateExpr = self.getStatisticsQueryBuilder(startDate, endDate)

        if dateExpr:
            cursor.execute(query, (0, location, startDate, endDate))
        else:
            cursor.execute(query, (0, location,))

        rows = cursor.fetchall()

        conn.close()

        return rows
        
    def getFalsePositivesForLocation(self, location, startDate, endDate):
        conn = pyodbc.connect(self.conn_str)

        cursor = conn.cursor()

        query, dateExpr = self.getStatisticsQueryBuilder(startDate, endDate)

        if dateExpr:
            cursor.execute(query, (1, location, startDate, endDate))
        else:
            cursor.execute(query, (1, location,))

        rows = cursor.fetchall()

        conn.close()

        return rows
        
    def getStatisticsQueryBuilder(self, startDate, endDate):
        dateExpr = ''

        if startDate is not None and endDate is not None:
            dateExpr = 'AND Date BETWEEN ? AND ?'
    
        query = '''
            SELECT Date, Count(*)
            FROM Accidents
            JOIN Locations loc ON loc.Id = LocationId
            WHERE isFalsePositive = ? and loc.Location = ? {}
            GROUP BY Date
            ORDER BY Date
        '''.format(dateExpr)

        return query, dateExpr
    
    def getLocations(self):
        conn = pyodbc.connect(self.conn_str)

        cursor = conn.cursor()

        cursor.execute("Select Location from Locations")

        rows = cursor.fetchall()

        conn.close()

        locations = [row[0] for row in rows]
        return locations
    
    def login(self, login, password):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        passwordHash = hashlib.sha256(password.encode()).hexdigest()
        print(passwordHash)

        cursor.execute("Select Id, PasswordHash, IdRole, IsPasswordExpired from Authentication where Login = ? and IsActive = 1", (login))

        result = cursor.fetchone()
        if result and result[0]:
            if passwordHash == result[1]:
                self.userId = result[0]
                cursor.execute("INSERT INTO AuthenticationLogs (AuthenticationId, Date, IsSuccessfull) values (?, ?, ?)", (result[0], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), True))
                conn.commit()
                conn.close()
                return True, result[2] == 1, result[0], result[3]
            else:
                cursor.execute("INSERT INTO AuthenticationLogs (AuthenticationId, Date, IsSuccessfull) values (?, ?, ?)", (result[0], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), False))
                conn.commit()
                conn.close()
                return False, False, None, False
        return False, False, None, False
    
    def register(self, login, password, useMail, useTelegram):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            passwordHash = hashlib.sha256(password.encode()).hexdigest()
            
            if useMail and not useTelegram:
                informType = 0
            elif not useMail and useTelegram:
                informType = 1
            elif useMail and useTelegram:
                informType = 2
            
            cursor.execute("INSERT INTO Authentication (Login, PasswordHash, IdRole, IsActive, IsPasswordExpired) values (?, ?, ?, ?, ?)", (login, passwordHash, 2, 1, 0))
            conn.commit()

            cursor.execute("Select Id from Authentication where Login = ? and IsActive = 1", (login))
            userId = cursor.fetchone()[0]

            cursor.execute("Insert into PreferedInformMethod (Method, AuthenticationId) values (?, ?)", (informType, userId,))
            conn.commit()
            telegramCode = None

            if informType == 1 or informType == 2:
                telegramCode = uuid.uuid4()

                cursor.execute("Insert into [TelegramAuthorizations] (AuthenticationId, [UniqueIdentifier]) values (?, ?)", (userId, telegramCode,))
                conn.commit()

            conn.close()
            return True, userId, telegramCode
        except:
            return False, None, None
        
    def updatePassword(self, login, password):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        passwordHash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("UPDATE Authentication set PasswordHash = ?, IsPasswordExpired = 0 where Login = ?", (passwordHash, login, ))
        conn.commit()

        cursor.execute("Select Id from Authentication where Login = ? and IsActive = 1", (login))
        userId = cursor.fetchone()[0]
        conn.close()

        return userId
        
    def getUserNames(self, userId):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()

        cursor.execute("Select Login from Authentication where Id != ?", (userId))
        results = cursor.fetchall()

        conn.close()

        names = [row[0] for row in results]

        return names
    
    def getRoleNames(self):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()

        cursor.execute("Select Name from Roles")

        results = cursor.fetchall()

        conn.close()
        names = [row[0] for row in results]

        return names
    
    def getRoleName(self, loginName):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()

        cursor.execute("Select r.Name from Roles r join Authentication a on a.IdRole = r.Id where a.Login = ? and a.IsActive = 1", (loginName,))

        result = cursor.fetchone()

        conn.close()

        return result[0]
    
    def deleteUser(self, loginName, adminId):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()

            cursor.execute("Update Authentication set IsActive = 0 WHERE Login = ? AND IdRole = 2", (loginName,))

            conn.commit()

            cursor.execute("Select Id from Authentication WHERE Login = ? and IsActive = 1", (loginName,))

            result = cursor.fetchone()

            if result[0] is not None:
                cursor.execute("Insert into UserDeletionLogs (DeletedId, DeletedById, DeletionDate) values (?, ?, ?)", (result[0], adminId, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                
            conn.close()
            
            return result[0] is not None
        except:
            return False
        
    def expirePassword(self, loginName):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("Update Authentication set IsPasswordExpired = 1 WHERE Login = ? AND IdRole = 2", (loginName,))

        conn.commit()
        conn.close()

    def updateRole(self, loginName, newRole):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("Select Id from Roles where Name = ?", (newRole,))
        newRoleId = cursor.fetchone()

        cursor.execute("Update Authentication set IdRole = ? WHERE Login = ?", (newRoleId[0], loginName,))

        conn.commit()
        conn.close()

    def insertTimeForAccidentReport(self, location, time, sendBy):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.execute("Select Id from locations where Location = ?", (location))
        location_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO [AccidentsTime] ([Date], [TimeForReport], [LocationId], SendBy) values (?, ?, ?, ?)", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), time, location_id, sendBy,))
        conn.commit()
        conn.close()

    def getIncidentTimeReactionStatistics(self, location, fromDate, toDate):
        conn = pyodbc.connect(self.conn_str)

        cursor = conn.cursor()

        query, dateExpr = self.getTimeStatisticsQueryBuilder(fromDate, toDate)

        if dateExpr:
            cursor.execute(query, (location, fromDate, toDate,))
        else:
            cursor.execute(query, (location,))

        rows = cursor.fetchall()

        conn.close()

        return rows
    
    def getTimeStatisticsQueryBuilder(self, startDate, endDate):
        dateExpr = ''

        if startDate is not None and endDate is not None:
            dateExpr = 'AND Date BETWEEN ? AND ?'
    
        query = '''
            SELECT AccidentsTime.Id, TimeForReport, SendBy
            FROM AccidentsTime
            JOIN Locations loc ON loc.Id = LocationId
            WHERE loc.Location = ? {}
            GROUP BY AccidentsTime.Id, TimeForReport, SendBy
            ORDER BY AccidentsTime.Id, TimeForReport, SendBy
        '''.format(dateExpr)

        return query, dateExpr
    
    def checkTelegramCode(self, telegramCode):
        conn = pyodbc.connect(self.conn_str)

        cursor = conn.cursor()

        cursor.execute("Select [AuthenticationId] from [TelegramAuthorizations] where [UniqueIdentifier] = ?", (telegramCode))

        userId = cursor.fetchone()[0]

        conn.close()

        return userId
    
    def saveUserChatId(self, chat_id, userId):
        conn = pyodbc.connect(self.conn_str)

        cursor = conn.cursor()
        cursor.execute("Insert into [AuthorizedTelegramUsers] (UserTelegramId, AuthenticationId) values (?, ?)", (chat_id, userId,))
        cursor.commit()

        conn.close()

    def getPrefferedInformationMethod(self, authenticationId):
        conn = pyodbc.connect(self.conn_str)

        cursor = conn.cursor()

        cursor.execute("Select [Method] from PreferedInformMethod where [AuthenticationId] = ?", (authenticationId,))

        prefferedMethod = cursor.fetchone()[0]

        return prefferedMethod
    
    def getChatIdByAuthenticationId(self, authenticationId):
        conn = pyodbc.connect(self.conn_str)

        cursor = conn.cursor()

        cursor.execute("Select [UserTelegramId] from [AuthorizedTelegramUsers] where [AuthenticationId] = ?", (authenticationId,))

        chatId = cursor.fetchone()[0]

        return chatId
