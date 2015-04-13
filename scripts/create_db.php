#!/usr/bin/env php
<?php

/************************************************************
*
* pfSense IndentityDB (pfSiDB)
*
* FILENAME:    create_db.php
* DESCRIPTION: This script creates the pfSiDB MySQL/MariaDB
*              database.
* 
* AUTHOR:      Patrick K. Ryon (slashdoom)
* LICENSE:     3 clause BSD (see LICENSE file)
*
***********************************************************/

  include("../include/config.inc.php");

  // Connect to SQL server
  $db_conn = mysqli_connect($db_host, $db_user, $db_pass);

  // Check SQL connection
  if (mysqli_connect_errno())
  {
    echo "Failed to connect to MySQL: ".mysqli_connect_error()."\n";
    $db_stat = false;
  }
  else {
    echo "Successfully connected to MySQL: ".$db_host."\n";
    $db_stat = true;
  }
    // Execute code ONLY if connections were successful
  if ($db_stat) {

    // Create SQL database
    $create_sql = "CREATE DATABASE ".$db_name;

    // Check SQL database
    if (mysqli_query($db_conn,$create_sql))  {
      echo "CREATE DATABASE ".$db_name." -  Successful.\n";
      
      // Build SQL query to create user_to_ip table
      $create_table_user_to_ip = "CREATE TABLE ".$db_name.".user_to_ip ( ";
      $create_table_user_to_ip .= "id INT NOT NULL AUTO_INCREMENT , PRIMARY KEY(id) , ";
      $create_table_user_to_ip .= "datetime TIMESTAMP NOT NULL , ";
      $create_table_user_to_ip .= "user VARCHAR( 50 ) NOT NULL , ";
      $create_table_user_to_ip .= "domain VARCHAR( 100 ) NOT NULL , ";
      $create_table_user_to_ip .= "ip VARCHAR( 39 ) NOT NULL, ";
      $create_table_user_to_ip .= "source VARCHAR( 50 ) ";
      $create_table_user_to_ip .= ")";

      // Execute create user_to_ip table SQL query and check results
      if (mysqli_query($db_conn,$create_table_user_to_ip))  {
        echo "CREATE TABLE user_to_ip -  Successful.\n";
      }
      else {
        echo "CREATE TABLE user_to_ip - Failed. ".mysqli_error($db_conn)."\n";
      }
      
      // Build SQL query to create user_groups table
      $create_table_user_groups = "CREATE TABLE ".$db_name.".user_groups ( ";
      $create_table_user_groups .= "id INT NOT NULL AUTO_INCREMENT , PRIMARY KEY(id) , ";
      $create_table_user_groups .= "datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP , ";
      $create_table_user_groups .= "user VARCHAR( 50 ) NOT NULL , ";
      $create_table_user_groups .= "domain VARCHAR( 100 ) NOT NULL , ";
      $create_table_user_groups .= "groups LONGTEXT ";
      $create_table_user_groups .= ")";

      // Execute create user_groups table SQL query and check results
      if (mysqli_query($db_conn,$create_table_user_groups))  {
        echo "CREATE TABLE user_groups -  Successful.\n";
      }
      else {
        echo "CREATE TABLE user_groups - Failed. ".mysqli_error($db_conn)."\n";
      }
    }
    else {
      echo "Create DATABASE ".$db_name."' - Failed.  ".mysqli_error($db_conn)."\n";
    }
  }
  
?>
