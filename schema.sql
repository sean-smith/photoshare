-- CREATE DATABASE photoshare;
USE photoshare;
DROP TABLE Photos CASCADE;
DROP TABLE Albums CASCADE;
DROP TABLE Friends CASCADE;
DROP TABLE Users CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    fname varchar(255),
    lname varchar(255),
    email varchar(255) UNIQUE,
    dob DATE,
    hometown varchar(255),
    gender varchar(7),  
    password varchar(255),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Photos
(
  picture_id int4  AUTO_INCREMENT,
  album_id int4,
  user_id int4,
  imgdata longblob,
  thumbnail longblob,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Albums
(
  album_id int4  AUTO_INCREMENT,
  name varchar(255),
  owner int4,
  doc DATE,
  thumbnail longblob,
  INDEX upid_idx (owner),
  CONSTRAINT albums_pk PRIMARY KEY (album_id)
);

CREATE TABLE Friends
(
  from_who int4,
  to_who int4,
  CONSTRAINT friends_pk PRIMARY KEY (from_who, to_who)
);

INSERT INTO Users (email, password, fname, lname, dob) VALUES ('swsmith@bu.edu', 'hi', 'Sean', 'Smith', '1995-06-20');
INSERT INTO Users (email, password, fname, lname, dob) VALUES ('test@bu.edu', 'test', 'Ann', 'Ming', '1995-06-20');

INSERT INTO Friends (from_who, to_who) VALUES (1,2);
INSERT INTO Friends (from_who, to_who) VALUES (2,1);
