-- =========================================================
-- GlobalWeatherDB - Database & Main Table
-- =========================================================

-- Create the database if it does not exist
IF DB_ID('GlobalWeatherDB') IS NULL
BEGIN
    CREATE DATABASE GlobalWeatherDB;
END;
GO

USE GlobalWeatherDB;
GO


-- =========================================================
-- Main Weather Readings Table
-- =========================================================

IF OBJECT_ID('dbo.WeatherReadings', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.WeatherReadings
    (
        WeatherReadingID INT IDENTITY(1,1) PRIMARY KEY,

        CityName NVARCHAR(100) NOT NULL,
        Country NVARCHAR(100) NOT NULL,

        Latitude DECIMAL(9,6) NOT NULL,
        Longitude DECIMAL(9,6) NOT NULL,

        TemperatureC DECIMAL(5,2) NULL,
        Humidity DECIMAL(5,2) NULL,
        WindSpeed DECIMAL(7,2) NULL,

        RecordedAt DATETIME2 NOT NULL,

        CONSTRAINT UQ_WeatherReadings_City_RecordedAt
            UNIQUE (CityName, RecordedAt),

        CONSTRAINT CK_WeatherReadings_Latitude
            CHECK (Latitude BETWEEN -90 AND 90),

        CONSTRAINT CK_WeatherReadings_Longitude
            CHECK (Longitude BETWEEN -180 AND 180),

        CONSTRAINT CK_WeatherReadings_Humidity
            CHECK (Humidity IS NULL OR Humidity BETWEEN 0 AND 100)
    );
END;
GO