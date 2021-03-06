/*
    for use in sqlite3 db, for test purposes
 */

CREATE TABLE APIGEE_MGMT_ENDPOINT (
    ID INTEGER PRIMARY KEY ASC,
    ENDPOINT_KEY TEXT,
    ENDPOINT TEXT
);

CREATE UNIQUE INDEX APIGEE_MGMT_ENDPOINT_EP on APIGEE_MGMT_ENDPOINT(ENDPOINT_KEY);

CREATE TABLE APIGEE_MGMT_LOG (
    ID INTEGER PRIMARY KEY ASC,
    TENANT_PREFIX TEXT,
    REQUEST_TEXT TEXT,
    RESPONSE_TEXT TEXT,
    IP_ADDR TEXT,
	USERNAME TEXT,
	CREATED_BY TEXT,
	CREATED_DATE TEXT,
	USER_ROLES TEXT,
	BUILD_TAGS TEXT,
	BUILD_COMMENT TEXT
);
