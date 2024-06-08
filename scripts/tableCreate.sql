Create table Classifications(
Id int primary key identity,
Name varchar(50))
go
create table Locations(
Id int primary key identity,
Location varchar(50))
go
create table Accidents(
Id int primary key identity,
LocationId int foreign key references Locations(Id),
ClassificationId int foreign key references Classifications(Id),
Incident VARBINARY (MAX),
Confidence float,
isFalsePositive int,
[Date] date)
go
create table Roles(
Id int primary key identity,
[Name] nvarchar(255) unique,
[CanEditFalsePositives] bit,
[CanChangeRoles] bit,
[CanDeleteUsers] bit
)
go
create table [Authentication](
Id int primary key identity,
[Login] nvarchar(255) unique not null,
[PasswordHash] nvarchar(255) not null,
IdRole int foreign key references Roles(Id) Not null,
IsActive bit not null,
IsPasswordExpired bit not null
)
go
create table [AuthenticationLogs](
Id int primary key identity,
AuthenticationId int foreign key references [Authentication](Id) not null,
[Date] datetime2 not null,
IsSuccessfull bit not null
)
go
create table [UserDeletionLogs](
Id int primary key identity,
DeletedId int foreign key references [Authentication](Id) not null,
DeletedById int foreign key references [Authentication](Id) not null,
DeletionDate datetime2 not null
)
go

Create table [AccidentsTime](
Id int primary key identity,
[Date] date not null,
[TimeForReport] float not null,
LocationId int foreign key references Locations(Id),
SendBy int
)
go

create table [TelegramAuthorizations](
Id int primary key identity,
AuthenticationId int foreign key references [Authentication](Id) not null,
[UniqueIdentifier] nvarchar (255) not null,
)
go

create table [AuthorizedTelegramUsers](
Id int primary key identity,
UserTelegramId nvarchar(255) not null,
AuthenticationId int foreign key references [Authentication](Id) not null,
)
go

create table PreferedInformMethod(
Id int primary key identity,
Method int not null,
AuthenticationId int foreign key references [Authentication](Id) not null
)
go