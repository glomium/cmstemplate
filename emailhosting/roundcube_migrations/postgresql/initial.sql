-- Roundcube Webmail initial database structure

--
-- Sequence "roundcube_users_seq"
-- Name: roundcube_users_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE roundcube_users_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

--
-- Table "roundcube_users"
-- Name: roundcube_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roundcube_users (
    user_id integer DEFAULT nextval('roundcube_users_seq'::text) PRIMARY KEY,
    username varchar(128) DEFAULT '' NOT NULL,
    mail_host varchar(128) DEFAULT '' NOT NULL,
    created timestamp with time zone DEFAULT now() NOT NULL,
    last_login timestamp with time zone DEFAULT NULL,
    failed_login timestamp with time zone DEFAULT NULL,
    failed_login_counter integer DEFAULT NULL,
    "language" varchar(5),
    preferences text DEFAULT ''::text NOT NULL,
    CONSTRAINT users_username_key UNIQUE (username, mail_host)
);


--
-- Table "roundcube_session"
-- Name: roundcube_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "roundcube_session" (
    sess_id varchar(128) DEFAULT '' PRIMARY KEY,
    created timestamp with time zone DEFAULT now() NOT NULL,
    changed timestamp with time zone DEFAULT now() NOT NULL,
    ip varchar(41) NOT NULL,
    vars text NOT NULL
);

CREATE INDEX session_changed_idx ON roundcube_session (changed);


--
-- Sequence "roundcube_identities_seq"
-- Name: roundcube_identities_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE roundcube_identities_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

--
-- Table "roundcube_identities"
-- Name: roundcube_identities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roundcube_identities (
    identity_id integer DEFAULT nextval('roundcube_identities_seq'::text) PRIMARY KEY,
    user_id integer NOT NULL
        REFERENCES roundcube_users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    changed timestamp with time zone DEFAULT now() NOT NULL,
    del smallint DEFAULT 0 NOT NULL,
    standard smallint DEFAULT 0 NOT NULL,
    name varchar(128) NOT NULL,
    organization varchar(128),
    email varchar(128) NOT NULL,
    "reply-to" varchar(128),
    bcc varchar(128),
    signature text,
    html_signature integer DEFAULT 0 NOT NULL
);

CREATE INDEX identities_user_id_idx ON roundcube_identities (user_id, del);
CREATE INDEX identities_email_idx ON roundcube_identities (email, del);


--
-- Sequence "roundcube_contacts_seq"
-- Name: roundcube_contacts_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE roundcube_contacts_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

--
-- Table "roundcube_contacts"
-- Name: roundcube_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roundcube_contacts (
    contact_id integer DEFAULT nextval('roundcube_contacts_seq'::text) PRIMARY KEY,
    user_id integer NOT NULL
        REFERENCES roundcube_users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    changed timestamp with time zone DEFAULT now() NOT NULL,
    del smallint DEFAULT 0 NOT NULL,
    name varchar(128) DEFAULT '' NOT NULL,
    email text DEFAULT '' NOT NULL,
    firstname varchar(128) DEFAULT '' NOT NULL,
    surname varchar(128) DEFAULT '' NOT NULL,
    vcard text,
    words text
);

CREATE INDEX contacts_user_id_idx ON roundcube_contacts (user_id, del);

--
-- Sequence "roundcube_contactgroups_seq"
-- Name: roundcube_contactgroups_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE roundcube_contactgroups_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

--
-- Table "roundcube_contactgroups"
-- Name: roundcube_contactgroups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roundcube_contactgroups (
    contactgroup_id integer DEFAULT nextval('roundcube_contactgroups_seq'::text) PRIMARY KEY,
    user_id integer NOT NULL
        REFERENCES roundcube_users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    changed timestamp with time zone DEFAULT now() NOT NULL,
    del smallint NOT NULL DEFAULT 0,
    name varchar(128) NOT NULL DEFAULT ''
);

CREATE INDEX contactgroups_user_id_idx ON roundcube_contactgroups (user_id, del);

--
-- Table "roundcube_contactgroupmembers"
-- Name: roundcube_contactgroupmembers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roundcube_contactgroupmembers (
    contactgroup_id integer NOT NULL
        REFERENCES roundcube_contactgroups(contactgroup_id) ON DELETE CASCADE ON UPDATE CASCADE,
    contact_id integer NOT NULL
        REFERENCES roundcube_contacts(contact_id) ON DELETE CASCADE ON UPDATE CASCADE,
    created timestamp with time zone DEFAULT now() NOT NULL,
    PRIMARY KEY (contactgroup_id, contact_id)
);

CREATE INDEX contactgroupmembers_contact_id_idx ON roundcube_contactgroupmembers (contact_id);

--
-- Table "roundcube_cache"
-- Name: roundcube_cache; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "roundcube_cache" (
    user_id integer NOT NULL
        REFERENCES roundcube_users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    cache_key varchar(128) DEFAULT '' NOT NULL,
    created timestamp with time zone DEFAULT now() NOT NULL,
    expires timestamp with time zone DEFAULT NULL,
    data text NOT NULL
);

CREATE INDEX cache_user_id_idx ON "roundcube_cache" (user_id, cache_key);
CREATE INDEX cache_expires_idx ON "roundcube_cache" (expires);

--
-- Table "roundcube_cache_shared"
-- Name: roundcube_cache_shared; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "roundcube_cache_shared" (
    cache_key varchar(255) NOT NULL,
    created timestamp with time zone DEFAULT now() NOT NULL,
    expires timestamp with time zone DEFAULT NULL,
    data text NOT NULL
);

CREATE INDEX cache_shared_cache_key_idx ON "roundcube_cache_shared" (cache_key);
CREATE INDEX cache_shared_expires_idx ON "roundcube_cache_shared" (expires);

--
-- Table "roundcube_cache_index"
-- Name: roundcube_cache_index; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roundcube_cache_index (
    user_id integer NOT NULL
        REFERENCES roundcube_users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    mailbox varchar(255) NOT NULL,
    expires timestamp with time zone DEFAULT NULL,
    valid smallint NOT NULL DEFAULT 0,
    data text NOT NULL,
    PRIMARY KEY (user_id, mailbox)
);

CREATE INDEX cache_index_expires_idx ON roundcube_cache_index (expires);

--
-- Table "roundcube_cache_thread"
-- Name: roundcube_cache_thread; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roundcube_cache_thread (
    user_id integer NOT NULL
        REFERENCES roundcube_users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    mailbox varchar(255) NOT NULL,
    expires timestamp with time zone DEFAULT NULL,
    data text NOT NULL,
    PRIMARY KEY (user_id, mailbox)
);

CREATE INDEX cache_thread_expires_idx ON roundcube_cache_thread (expires);

--
-- Table "roundcube_cache_messages"
-- Name: roundcube_cache_messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roundcube_cache_messages (
    user_id integer NOT NULL
        REFERENCES roundcube_users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    mailbox varchar(255) NOT NULL,
    uid integer NOT NULL,
    expires timestamp with time zone DEFAULT NULL,
    data text NOT NULL,
    flags integer NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, mailbox, uid)
);

CREATE INDEX cache_messages_expires_idx ON roundcube_cache_messages (expires);

--
-- Table "roundcube_dictionary"
-- Name: roundcube_dictionary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roundcube_dictionary (
    user_id integer DEFAULT NULL
        REFERENCES roundcube_users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
   "language" varchar(5) NOT NULL,
    data text NOT NULL,
    CONSTRAINT dictionary_user_id_language_key UNIQUE (user_id, "language")
);

--
-- Sequence "roundcube_searches_seq"
-- Name: roundcube_searches_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE roundcube_searches_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

--
-- Table "roundcube_searches"
-- Name: roundcube_searches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roundcube_searches (
    search_id integer DEFAULT nextval('roundcube_searches_seq'::text) PRIMARY KEY,
    user_id integer NOT NULL
        REFERENCES roundcube_users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    "type" smallint DEFAULT 0 NOT NULL,
    name varchar(128) NOT NULL,
    data text NOT NULL,
    CONSTRAINT searches_user_id_key UNIQUE (user_id, "type", name)
);


--
-- Table "roundcube_system"
-- Name: roundcube_system; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "roundcube_system" (
    name varchar(64) NOT NULL PRIMARY KEY,
    value text
);

INSERT INTO roundcube_system (name, value) VALUES ('roundcube-version', '2015111100');
