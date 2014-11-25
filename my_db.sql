--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: postgres; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON DATABASE postgres IS 'default administrative connection database';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: adminpack; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS adminpack WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION adminpack; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION adminpack IS 'administrative functions for PostgreSQL';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: onair_program; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE onair_program (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    scheduledprogram_id integer,
    episode_id integer
);


ALTER TABLE public.onair_program OWNER TO postgres;

--
-- Name: onair_program_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE onair_program_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.onair_program_id_seq OWNER TO postgres;

--
-- Name: onair_program_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE onair_program_id_seq OWNED BY onair_program.id;


--
-- Name: radio_episode; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_episode (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    program_id integer NOT NULL,
    recording_id integer
);


ALTER TABLE public.radio_episode OWNER TO postgres;

--
-- Name: radio_episode_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_episode_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_episode_id_seq OWNER TO postgres;

--
-- Name: radio_episode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_episode_id_seq OWNED BY radio_episode.id;


--
-- Name: radio_incominggateway; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_incominggateway (
    incominggateway_id integer,
    station_id integer
);


ALTER TABLE public.radio_incominggateway OWNER TO postgres;

--
-- Name: radio_language; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_language (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    name character varying(100),
    iso639_1 character varying(2),
    iso639_2 character varying(3),
    locale_code character varying(10)
);


ALTER TABLE public.radio_language OWNER TO postgres;

--
-- Name: radio_language_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_language_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_language_id_seq OWNER TO postgres;

--
-- Name: radio_language_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_language_id_seq OWNED BY radio_language.id;


--
-- Name: radio_location; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_location (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    name character varying(100),
    municipality character varying(100),
    district character varying(100),
    country character varying(100),
    addressline1 character varying(100),
    addressline2 character varying(100),
    latitude double precision,
    longitude double precision
);


ALTER TABLE public.radio_location OWNER TO postgres;

--
-- Name: radio_location_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_location_id_seq OWNER TO postgres;

--
-- Name: radio_location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_location_id_seq OWNED BY radio_location.id;


--
-- Name: radio_network; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_network (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    name character varying(100) NOT NULL,
    about text
);


ALTER TABLE public.radio_network OWNER TO postgres;

--
-- Name: radio_network_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_network_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_network_id_seq OWNER TO postgres;

--
-- Name: radio_network_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_network_id_seq OWNED BY radio_network.id;


--
-- Name: radio_networkadmins; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_networkadmins (
    user_id integer,
    network_id integer
);


ALTER TABLE public.radio_networkadmins OWNER TO postgres;

--
-- Name: radio_networkpadding; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_networkpadding (
    network_id integer,
    paddingcontent_id integer
);


ALTER TABLE public.radio_networkpadding OWNER TO postgres;

--
-- Name: radio_outgoinggateway; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_outgoinggateway (
    outgoinggateway_id integer,
    station_id integer
);


ALTER TABLE public.radio_outgoinggateway OWNER TO postgres;

--
-- Name: radio_paddingcontent; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_paddingcontent (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    recording_id integer,
    block_id integer
);


ALTER TABLE public.radio_paddingcontent OWNER TO postgres;

--
-- Name: radio_paddingcontent_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_paddingcontent_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_paddingcontent_id_seq OWNER TO postgres;

--
-- Name: radio_paddingcontent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_paddingcontent_id_seq OWNED BY radio_paddingcontent.id;


--
-- Name: radio_person; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_person (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    title character varying(8),
    firstname character varying(100),
    middlename character varying(100),
    lastname character varying(100),
    email character varying(100),
    additionalcontact character varying(100),
    phone_id integer,
    gender_code integer,
    privacy_code integer
);


ALTER TABLE public.radio_person OWNER TO postgres;

--
-- Name: radio_person_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_person_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_person_id_seq OWNER TO postgres;

--
-- Name: radio_person_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_person_id_seq OWNED BY radio_person.id;


--
-- Name: radio_personlanguage; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_personlanguage (
    language_id integer,
    person_id integer
);


ALTER TABLE public.radio_personlanguage OWNER TO postgres;

--
-- Name: radio_program; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_program (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    duration interval,
    update_recurrence text,
    language_id integer,
    program_type_id integer
);


ALTER TABLE public.radio_program OWNER TO postgres;

--
-- Name: radio_program_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_program_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_program_id_seq OWNER TO postgres;

--
-- Name: radio_program_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_program_id_seq OWNED BY radio_program.id;


--
-- Name: radio_programtype; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_programtype (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    name character varying(100) NOT NULL,
    description text NOT NULL,
    definition text NOT NULL,
    phone_functions text NOT NULL
);


ALTER TABLE public.radio_programtype OWNER TO postgres;

--
-- Name: radio_programtype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_programtype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_programtype_id_seq OWNER TO postgres;

--
-- Name: radio_programtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_programtype_id_seq OWNED BY radio_programtype.id;


--
-- Name: radio_recording; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_recording (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    url character varying(160),
    local_file character varying
);


ALTER TABLE public.radio_recording OWNER TO postgres;

--
-- Name: radio_recording_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_recording_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_recording_id_seq OWNER TO postgres;

--
-- Name: radio_recording_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_recording_id_seq OWNED BY radio_recording.id;


--
-- Name: radio_role; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_role (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    name character varying,
    person_id integer,
    station_id integer
);


ALTER TABLE public.radio_role OWNER TO postgres;

--
-- Name: radio_role_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_role_id_seq OWNER TO postgres;

--
-- Name: radio_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_role_id_seq OWNED BY radio_role.id;


--
-- Name: radio_scheduledblock; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_scheduledblock (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    name character varying(100) NOT NULL,
    recurrence text,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    station_id integer
);


ALTER TABLE public.radio_scheduledblock OWNER TO postgres;

--
-- Name: radio_scheduledblock_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_scheduledblock_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_scheduledblock_id_seq OWNER TO postgres;

--
-- Name: radio_scheduledblock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_scheduledblock_id_seq OWNED BY radio_scheduledblock.id;


--
-- Name: radio_scheduledprogram; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_scheduledprogram (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    station_id integer,
    program_id integer,
    start timestamp with time zone NOT NULL,
    "end" timestamp with time zone NOT NULL
);


ALTER TABLE public.radio_scheduledprogram OWNER TO postgres;

--
-- Name: radio_scheduledprogram_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_scheduledprogram_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_scheduledprogram_id_seq OWNER TO postgres;

--
-- Name: radio_scheduledprogram_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_scheduledprogram_id_seq OWNED BY radio_scheduledprogram.id;


--
-- Name: radio_station; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_station (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    name character varying(100) NOT NULL,
    about text,
    frequency double precision,
    api_key character varying(100) NOT NULL,
    owner_id integer,
    network_id integer,
    location_id integer,
    cloud_phone_id integer,
    transmitter_phone_id integer,
    broadcast_ip character varying(16),
    client_update_frequency double precision,
    timezone character varying(32),
    analytic_update_frequency double precision
);


ALTER TABLE public.radio_station OWNER TO postgres;

--
-- Name: radio_station_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_station_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_station_id_seq OWNER TO postgres;

--
-- Name: radio_station_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_station_id_seq OWNED BY radio_station.id;


--
-- Name: radio_stationanalytic; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_stationanalytic (
    id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    station_id integer,
    battery_level double precision,
    cpu_load double precision,
    memory_utilization double precision,
    storage_usage double precision,
    headphone_plug boolean,
    gps_lat double precision,
    gps_lon double precision,
    gsm_signal double precision,
    wifi_connected boolean
);


ALTER TABLE public.radio_stationanalytic OWNER TO postgres;

--
-- Name: radio_stationanalytic_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE radio_stationanalytic_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radio_stationanalytic_id_seq OWNER TO postgres;

--
-- Name: radio_stationanalytic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE radio_stationanalytic_id_seq OWNED BY radio_stationanalytic.id;


--
-- Name: radio_stationlanguage; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE radio_stationlanguage (
    language_id integer,
    station_id integer
);


ALTER TABLE public.radio_stationlanguage OWNER TO postgres;

--
-- Name: telephony_call; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE telephony_call (
    id integer NOT NULL,
    call_uuid character varying(100),
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    from_phonenumber_id integer,
    to_phonenumber_id integer,
    a_leg_uuid character varying(100),
    a_leg_request_uuid character varying(100),
    onairprogram_id integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.telephony_call OWNER TO postgres;

--
-- Name: telephony_call_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE telephony_call_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.telephony_call_id_seq OWNER TO postgres;

--
-- Name: telephony_call_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE telephony_call_id_seq OWNED BY telephony_call.id;


--
-- Name: telephony_gateway; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE telephony_gateway (
    id integer NOT NULL,
    number_top integer,
    number_bottom integer,
    sofia_string character varying(160),
    extra_string character varying(300),
    name character varying(100),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    is_goip boolean,
    gateway_prefix character varying(20)
);


ALTER TABLE public.telephony_gateway OWNER TO postgres;

--
-- Name: telephony_gateway_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE telephony_gateway_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.telephony_gateway_id_seq OWNER TO postgres;

--
-- Name: telephony_gateway_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE telephony_gateway_id_seq OWNED BY telephony_gateway.id;


--
-- Name: telephony_message; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE telephony_message (
    id integer NOT NULL,
    message_uuid character varying(100),
    sendtime timestamp without time zone,
    text character varying(160),
    from_phonenumber_id integer,
    to_phonenumber_id integer,
    onairprogram_id integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.telephony_message OWNER TO postgres;

--
-- Name: telephony_message_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE telephony_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.telephony_message_id_seq OWNER TO postgres;

--
-- Name: telephony_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE telephony_message_id_seq OWNED BY telephony_message.id;


--
-- Name: telephony_phonenumber; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE telephony_phonenumber (
    id integer NOT NULL,
    carrier character varying(100),
    countrycode character varying(3),
    number character varying(20) NOT NULL,
    raw_number character varying(20),
    number_type integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.telephony_phonenumber OWNER TO postgres;

--
-- Name: telephony_phonenumber_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE telephony_phonenumber_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.telephony_phonenumber_id_seq OWNER TO postgres;

--
-- Name: telephony_phonenumber_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE telephony_phonenumber_id_seq OWNED BY telephony_phonenumber.id;


--
-- Name: user_details; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_details (
    id integer NOT NULL,
    age integer,
    phone character varying(100),
    url character varying(100),
    location character varying(100),
    bio character varying(100),
    gender_code integer,
    created_time timestamp without time zone
);


ALTER TABLE public.user_details OWNER TO postgres;

--
-- Name: user_details_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE user_details_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_details_id_seq OWNER TO postgres;

--
-- Name: user_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE user_details_id_seq OWNED BY user_details.id;


--
-- Name: user_user; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_user (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    openid character varying(100),
    activation_key character varying(100),
    created_time timestamp without time zone,
    last_accessed timestamp without time zone,
    avatar character varying(100),
    password character varying(300) NOT NULL,
    role_code smallint,
    status_code smallint,
    user_detail_id integer
);


ALTER TABLE public.user_user OWNER TO postgres;

--
-- Name: user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_user_id_seq OWNER TO postgres;

--
-- Name: user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE user_user_id_seq OWNED BY user_user.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY onair_program ALTER COLUMN id SET DEFAULT nextval('onair_program_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_episode ALTER COLUMN id SET DEFAULT nextval('radio_episode_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_language ALTER COLUMN id SET DEFAULT nextval('radio_language_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_location ALTER COLUMN id SET DEFAULT nextval('radio_location_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_network ALTER COLUMN id SET DEFAULT nextval('radio_network_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_paddingcontent ALTER COLUMN id SET DEFAULT nextval('radio_paddingcontent_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_person ALTER COLUMN id SET DEFAULT nextval('radio_person_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_program ALTER COLUMN id SET DEFAULT nextval('radio_program_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_programtype ALTER COLUMN id SET DEFAULT nextval('radio_programtype_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_recording ALTER COLUMN id SET DEFAULT nextval('radio_recording_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_role ALTER COLUMN id SET DEFAULT nextval('radio_role_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_scheduledblock ALTER COLUMN id SET DEFAULT nextval('radio_scheduledblock_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_scheduledprogram ALTER COLUMN id SET DEFAULT nextval('radio_scheduledprogram_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_station ALTER COLUMN id SET DEFAULT nextval('radio_station_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_stationanalytic ALTER COLUMN id SET DEFAULT nextval('radio_stationanalytic_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY telephony_call ALTER COLUMN id SET DEFAULT nextval('telephony_call_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY telephony_gateway ALTER COLUMN id SET DEFAULT nextval('telephony_gateway_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY telephony_message ALTER COLUMN id SET DEFAULT nextval('telephony_message_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY telephony_phonenumber ALTER COLUMN id SET DEFAULT nextval('telephony_phonenumber_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_details ALTER COLUMN id SET DEFAULT nextval('user_details_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_user ALTER COLUMN id SET DEFAULT nextval('user_user_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY alembic_version (version_num) FROM stdin;
54068667be18
\.


--
-- Data for Name: onair_program; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY onair_program (id, created_at, updated_at, scheduledprogram_id, episode_id) FROM stdin;
\.


--
-- Name: onair_program_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('onair_program_id_seq', 1, false);


--
-- Data for Name: radio_episode; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_episode (id, created_at, updated_at, program_id, recording_id) FROM stdin;
\.


--
-- Name: radio_episode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_episode_id_seq', 1, false);


--
-- Data for Name: radio_incominggateway; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_incominggateway (incominggateway_id, station_id) FROM stdin;
1	5
1	3
\.


--
-- Data for Name: radio_language; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_language (id, created_at, updated_at, name, iso639_1, iso639_2, locale_code) FROM stdin;
1	2014-03-13 00:58:24.849479	2014-03-13 00:58:24.849494	English	en	eng	en_UG
2	2014-03-13 00:58:24.85113	2014-03-13 00:58:24.851136	Luganda	lg	lug	lg_UG
3	2014-03-14 00:33:58.303928	2014-03-14 00:33:58.303937	Nyankore		nyn	
4	2014-03-14 00:34:10.167301	2014-03-14 00:34:10.167313	Karamjong		kdj	
5	2014-03-14 00:34:22.58019	2014-03-14 00:34:22.5802	Ma'di		mhd	
6	2014-03-14 00:34:34.05175	2014-03-14 00:34:34.051761	Luo		luo	
\.


--
-- Name: radio_language_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_language_id_seq', 6, true);


--
-- Data for Name: radio_location; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_location (id, created_at, updated_at, name, municipality, district, country, addressline1, addressline2, latitude, longitude) FROM stdin;
2	2014-03-13 17:32:25.158302	2014-03-13 17:32:25.158315	Ibanda	Ibanda	Ibanda	Uganda	\N	\N	0.119999999999999996	30.5
3	2014-03-13 17:32:25.163386	2014-03-13 17:32:25.163395	Metuli	Metuli	Metuli	Uganda	\N	\N	3.71281099999999986	31.7833450000000006
4	2014-03-13 17:32:25.165112	2014-03-13 17:32:25.165119	Alero	Alero		Uganda	\N	\N	2.69578400000000018	32.0292770000000004
5	2014-03-13 17:32:25.1668	2014-03-13 17:32:25.166808	Mugongo	Mugongo		Uganda	\N	\N	1.16183900000000007	32.8152940000000015
6	2014-03-13 17:32:25.168632	2014-03-13 17:32:25.16864	Aber	Aber		Uganda	\N	\N	2.3162370000000001	32.686708000000003
7	2014-03-13 17:32:25.170597	2014-03-13 17:32:25.170604	Tam Pi Diki	Tam Pi Diki	Gulu	Uganda	\N	\N	2.63471600000000006	31.9975090000000009
8	2014-03-13 17:39:39.175524	2014-03-13 17:39:39.175866	Pabo	Pabo		Uganda			3.00167010000000012	32.1443652999999969
\.


--
-- Name: radio_location_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_location_id_seq', 8, true);


--
-- Data for Name: radio_network; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_network (id, created_at, updated_at, name, about) FROM stdin;
\.


--
-- Name: radio_network_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_network_id_seq', 1, false);


--
-- Data for Name: radio_networkadmins; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_networkadmins (user_id, network_id) FROM stdin;
\.


--
-- Data for Name: radio_networkpadding; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_networkpadding (network_id, paddingcontent_id) FROM stdin;
\.


--
-- Data for Name: radio_outgoinggateway; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_outgoinggateway (outgoinggateway_id, station_id) FROM stdin;
1	5
1	6
1	3
\.


--
-- Data for Name: radio_paddingcontent; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_paddingcontent (id, created_at, updated_at, recording_id, block_id) FROM stdin;
\.


--
-- Name: radio_paddingcontent_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_paddingcontent_id_seq', 1, false);


--
-- Data for Name: radio_person; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_person (id, created_at, updated_at, title, firstname, middlename, lastname, email, additionalcontact, phone_id, gender_code, privacy_code) FROM stdin;
1	2014-04-30 20:46:18	2014-04-30 20:46:18	Director	Christopher	Paul	Csikszentmihalyi	robotic@gmail.com		274	1	\N
2	2014-04-30 20:46:18	2014-04-30 20:46:18	CTO	Jude	Love	Mukundane	jude.mukundane@gmail.com		276	1	\N
3	2014-04-30 20:46:17	2014-04-30 20:46:17	Mr.	Josh		Levinger	josh@levinger.net		277	1	\N
\.


--
-- Name: radio_person_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_person_id_seq', 3, true);


--
-- Data for Name: radio_personlanguage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_personlanguage (language_id, person_id) FROM stdin;
2	2
3	2
1	3
\.


--
-- Data for Name: radio_program; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_program (id, created_at, updated_at, name, description, duration, update_recurrence, language_id, program_type_id) FROM stdin;
1	2014-03-14 00:36:36.189957	2014-03-14 00:36:36.189968	Vet Talk	Call in and ask a Vet about your pet.	00:30:00	\N	1	2
3	2014-03-14 00:38:16.138753	2014-03-14 00:38:16.138763	Morning paper (English)	Morning news read in English	00:10:00	\N	1	1
4	2014-03-14 00:38:38.456081	2014-03-14 00:38:38.456092	Morning news (Luo)	Morning news, read in Luo	00:05:00	\N	6	1
2	2014-03-14 00:37:26.461886	2014-03-14 00:39:46.793833	Informed Discussion	Experts discuss the news of the day	01:00:00	\N	1	3
\.


--
-- Name: radio_program_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_program_id_seq', 4, true);


--
-- Data for Name: radio_programtype; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_programtype (id, created_at, updated_at, name, description, definition, phone_functions) FROM stdin;
2	2014-03-14 00:32:39.563289	2014-04-30 20:41:46.138777	Call-in Show	Call in and talk to the host	""	""
1	2014-03-14 00:32:08.889955	2014-04-30 20:41:54.845615	Hourly News	Nothing but news. Every hour, on the hour.	""	""
3	2014-03-14 00:33:02.054414	2014-04-30 20:46:53.166337	Roundtable	Discussion with bright minds	"{'hey there':'this is json'}"	["this is json"]
\.


--
-- Name: radio_programtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_programtype_id_seq', 3, true);


--
-- Data for Name: radio_recording; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_recording (id, created_at, updated_at, url, local_file) FROM stdin;
\.


--
-- Name: radio_recording_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_recording_id_seq', 1, false);


--
-- Data for Name: radio_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_role (id, created_at, updated_at, name, person_id, station_id) FROM stdin;
\.


--
-- Name: radio_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_role_id_seq', 1, false);


--
-- Data for Name: radio_scheduledblock; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_scheduledblock (id, created_at, updated_at, name, recurrence, start_time, end_time, station_id) FROM stdin;
2	2014-03-13 22:24:29.244898	2014-03-14 00:31:33.224176	Weekday Mornings	FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR	06:00:00	10:00:00	2
3	2014-03-14 00:35:31.025502	2014-03-14 00:35:31.025516	Sunday Morning	FREQ=WEEKLY;BYDAY=SU	08:00:00	12:00:00	2
\.


--
-- Name: radio_scheduledblock_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_scheduledblock_id_seq', 3, true);


--
-- Data for Name: radio_scheduledprogram; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_scheduledprogram (id, created_at, updated_at, station_id, program_id, start, "end") FROM stdin;
6	2014-03-14 00:47:03.060447	2014-03-14 00:55:58.978598	2	3	2014-03-14 07:00:00+00	2014-03-14 07:10:00+00
8	2014-03-14 00:57:06.552293	2014-03-14 00:57:06.552302	2	2	2014-03-14 07:30:00+00	2014-03-14 08:30:00+00
9	2014-03-14 00:58:49.187781	2014-03-14 00:58:49.187791	2	1	2014-03-14 09:00:00+00	2014-03-14 09:30:00+00
7	2014-03-14 00:56:33.267969	2014-03-14 00:59:38.831875	2	4	2014-03-14 07:00:00+00	2014-03-14 07:05:00+00
11	2014-04-26 21:22:37.510327	2014-04-26 21:22:37.510335	6	3	2014-04-26 07:00:00+00	2014-04-26 07:10:00+00
10	2014-04-26 21:17:50.195157	2014-04-30 02:08:36.68255	6	2	2014-04-27 12:00:00+00	2014-04-27 13:00:00+00
12	2014-04-26 21:23:07.410298	2014-04-30 02:09:11.397687	6	1	2014-04-20 09:00:00+00	2014-04-20 09:30:00+00
13	2014-04-30 02:14:26.721809	2014-05-01 03:01:50.44135	\N	3	2014-04-28 07:30:00+00	2014-04-28 07:40:00+00
14	2014-04-30 02:15:53.069244	2014-05-01 03:01:50.44215	\N	4	2014-04-27 07:30:00+00	2014-04-27 07:35:00+00
15	2014-04-30 02:15:53.069639	2014-05-01 03:01:50.442581	\N	3	2014-05-01 09:00:00+00	2014-05-01 09:10:00+00
16	2014-04-30 02:18:37.118278	2014-05-01 03:01:50.442979	\N	3	2014-04-28 07:30:00+00	2014-04-28 07:40:00+00
17	2014-04-30 02:18:37.124513	2014-05-01 03:01:50.443355	\N	4	2014-04-27 07:30:00+00	2014-04-27 07:35:00+00
18	2014-04-30 02:18:37.131057	2014-05-01 03:01:50.443725	\N	2	2014-04-27 08:30:00+00	2014-04-27 09:30:00+00
19	2014-04-30 05:03:41.854614	2014-05-01 03:01:50.444094	\N	4	2014-05-01 07:00:00+00	2014-05-01 07:05:00+00
20	2014-04-30 05:04:00.51235	2014-05-01 03:01:50.444555	\N	4	2014-05-01 07:00:00+00	2014-05-01 07:05:00+00
21	2014-04-30 05:04:05.180896	2014-05-01 03:01:50.444957	\N	4	2014-05-01 07:00:00+00	2014-05-01 07:05:00+00
22	2014-04-30 05:29:05.217405	2014-05-01 03:01:50.445342	\N	4	2014-05-01 07:00:00+00	2014-05-01 07:05:00+00
23	2014-04-30 05:29:08.96812	2014-05-01 03:01:50.445743	\N	4	2014-05-01 07:00:00+00	2014-05-01 07:05:00+00
\.


--
-- Name: radio_scheduledprogram_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_scheduledprogram_id_seq', 23, true);


--
-- Data for Name: radio_station; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_station (id, created_at, updated_at, name, about, frequency, api_key, owner_id, network_id, location_id, cloud_phone_id, transmitter_phone_id, broadcast_ip, client_update_frequency, timezone, analytic_update_frequency) FROM stdin;
2	2014-03-13 17:32:25	2014-04-26 21:17:17.556339	Radio Aber		88.5	q0hMmMm1Pg	1	\N	6	\N	\N		\N	Africa/Kampala	\N
8	2014-03-13 17:32:25	2014-04-26 21:17:24.902768	Tom Pi Diki FM		95.5	YK07ydo4Ph	1	\N	7	\N	\N		\N	Africa/Kampala	\N
5	2014-03-13 17:32:25	2014-04-30 06:10:23.460449	Metuli RootIO		102.599999999999994	U3gfFkbuSn	1	\N	3	\N	274		\N	Africa/Kampala	\N
7	2014-03-13 17:32:25	2014-05-01 02:47:44.946724	Mugongo Farm Fresh SACCO		102.599999999999994	boJJ4nXvrk	1	\N	5	\N	25		\N	Africa/Kampala	\N
6	2014-03-13 17:32:25	2014-05-01 03:01:35.339549	Alero Community Radio		102.599999999999994	9d2mm19DQt	1	\N	4	276	276		\N	Africa/Kampala	\N
3	2014-03-13 17:32:25	2014-05-01 03:02:14.446558	Pabo FM		89	216XIot742	1	\N	8	277	277		\N	Africa/Kampala	\N
\.


--
-- Name: radio_station_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_station_id_seq', 9, true);


--
-- Data for Name: radio_stationanalytic; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_stationanalytic (id, created_at, updated_at, station_id, battery_level, cpu_load, memory_utilization, storage_usage, headphone_plug, gps_lat, gps_lon, gsm_signal, wifi_connected) FROM stdin;
1	2014-04-27 21:02:22.48308	2014-04-27 21:02:22.483147	6	50	\N	\N	\N	f	\N	\N	100	f
2	2014-04-27 21:02:24.048801	2014-04-27 21:02:24.048856	6	50	\N	\N	\N	f	\N	\N	100	f
3	2014-04-27 21:02:22.48308	2014-04-27 21:02:22.483147	6	50	10	75	25	t	-118.480850000000004	34.0138419999999968	100	t
4	2014-04-27 21:02:22.48308	2014-04-27 21:02:22.483147	2	\N	\N	\N	\N	f	\N	\N	\N	f
5	2014-04-27 21:02:22.48308	2014-04-27 21:02:22.483147	2	50	10	75	25	t	-118.480850000000004	34.0138419999999968	100	t
6	2014-04-27 21:02:22.48308	2014-04-27 21:02:22.483147	2	50	10	75	25	t	-118.480850000000004	34.0138419999999968	100	t
7	2014-04-27 21:02:24.048801	2014-04-27 21:02:24.048856	2	50	10	75	25	t	-118.480850000000004	34.0138419999999968	100	t
8	2014-04-27 21:02:24.048801	2014-04-27 21:02:24.048856	2	50	10	75	25	t	-118.480850000000004	34.0138419999999968	100	t
9	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
10	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
11	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
12	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
13	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
14	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
15	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
16	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
17	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
18	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
19	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
20	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
21	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
22	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
23	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
24	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
25	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
26	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
27	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
28	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
29	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
30	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
31	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
32	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
33	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
34	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
35	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
36	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
37	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
38	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
39	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
40	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
41	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
42	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
43	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
44	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
45	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
46	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
47	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
48	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
49	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
50	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
51	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
52	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
53	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
54	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
55	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
56	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
57	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
58	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
59	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
60	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
61	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
62	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
63	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
64	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
65	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
66	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
67	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
68	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
69	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
70	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
71	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
72	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
73	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
74	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
75	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
76	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
77	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
78	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
79	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
80	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
81	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
82	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
83	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
84	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
85	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
86	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
87	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
88	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
89	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
90	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
91	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
92	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
93	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
94	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
95	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
96	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
97	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
98	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
99	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
100	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
101	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
102	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
103	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
104	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
105	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
106	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
107	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
108	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
109	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
110	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
111	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
112	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
113	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
114	2014-04-28 02:27:08.566005	2014-04-28 02:27:08.56607	2	\N	\N	\N	\N	f	\N	\N	\N	f
115	2014-04-28 02:27:09.968668	2014-04-28 02:27:09.968733	2	\N	\N	\N	\N	f	\N	\N	\N	f
116	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
117	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
118	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
119	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
120	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
121	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
122	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
123	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
124	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
125	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
126	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
127	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
128	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
129	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
130	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
131	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
132	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
133	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
134	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
135	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
136	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
137	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
138	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
139	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
140	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
141	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
142	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
143	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
144	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
145	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
146	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
147	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
148	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
149	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
150	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
151	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
152	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
153	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
154	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
155	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
156	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
157	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
158	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
159	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
160	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
161	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
162	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
163	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
164	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
165	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
166	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
167	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
168	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
169	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
170	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
171	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
172	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
173	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
174	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
175	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
176	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
177	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
178	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
179	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
180	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
181	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
182	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
183	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
184	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
185	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
186	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
187	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
188	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
189	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
190	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
191	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
192	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
193	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
194	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
195	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
196	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
197	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
198	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
199	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
200	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
201	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
202	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
203	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
204	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
205	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
206	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
207	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
208	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
209	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
210	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
211	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
212	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
213	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
214	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
215	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
216	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
217	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
218	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
219	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
220	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
221	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
222	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
223	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
224	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
225	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
226	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
227	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
228	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
229	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
230	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
231	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
232	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
233	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
234	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
235	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
239	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
243	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
247	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
251	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
255	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
257	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
261	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
265	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
269	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
274	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
278	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
281	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
236	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
242	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
248	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
254	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
262	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
268	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
273	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
279	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
237	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
241	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
245	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
249	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
253	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
256	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
259	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
263	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
267	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
271	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
276	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
280	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
283	2014-04-29 19:27:51.394618	2014-04-29 19:27:51.394692	2	\N	\N	\N	\N	f	\N	\N	\N	f
238	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
244	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
250	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
258	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
264	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
270	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
275	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
282	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
240	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
246	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
252	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
260	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
266	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
272	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
277	2014-04-29 19:27:49.051533	2014-04-29 19:27:49.051591	2	\N	\N	\N	\N	f	\N	\N	\N	f
\.


--
-- Name: radio_stationanalytic_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('radio_stationanalytic_id_seq', 283, true);


--
-- Data for Name: radio_stationlanguage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY radio_stationlanguage (language_id, station_id) FROM stdin;
1	5
1	6
\.


--
-- Data for Name: telephony_call; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY telephony_call (id, call_uuid, start_time, end_time, from_phonenumber_id, to_phonenumber_id, a_leg_uuid, a_leg_request_uuid, onairprogram_id, created_at, updated_at) FROM stdin;
326	2be3c88c-d031-11e3-a9a9-ddcdf41f8136	2014-04-30 06:32:20.273964	2014-04-30 06:32:33.383726	275	274	\N	\N	\N	2014-04-30 06:32:20.227429+00	2014-04-30 06:32:33.384668+00
327	5e0bf8f0-d0dd-11e3-aa1a-ddcdf41f8136	2014-05-01 03:04:57.294147	2014-05-01 03:05:09.178273	275	274	\N	\N	\N	2014-05-01 03:04:57.257165+00	2014-05-01 03:05:09.179224+00
328	9b5ae5b8-d0dd-11e3-aa2c-ddcdf41f8136	2014-05-01 03:06:37.897751	2014-05-01 03:06:56.121861	275	277	\N	\N	\N	2014-05-01 03:06:37.896469+00	2014-05-01 03:06:56.122489+00
330		\N	2014-05-01 03:07:03.033649	\N	\N	\N	\N	\N	2014-05-01 03:06:56.040075+00	2014-05-01 03:07:03.034345+00
329	9f4fbe14-d0dd-11e3-aa30-ddcdf41f8136	2014-05-01 03:06:49.656114	2014-05-01 03:07:03.05292	275	276	\N	\N	\N	2014-05-01 03:06:49.654639+00	2014-05-01 03:07:03.053577+00
38	fbae34c6-ab06-11e3-a430-2d3cb1fb0bbd	\N	2014-03-13 23:27:09.198086	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
1	9e05bd82-aaf0-11e3-a0fc-2d3cb1fb0bbd	\N	2014-03-13 20:48:06.238842	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
28	0cf42f96-ab03-11e3-a35c-2d3cb1fb0bbd	\N	2014-03-13 22:58:54.261805	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
29	248006bc-ab03-11e3-a371-2d3cb1fb0bbd	\N	2014-03-13 22:59:37.370022	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
2	b3484f6a-aaf1-11e3-a10f-2d3cb1fb0bbd	2014-03-13 20:54:47.264055	2014-03-13 20:55:06.363695	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
27	8637a6d6-ab02-11e3-a32a-2d3cb1fb0bbd	2014-03-13 22:55:12.323464	2014-03-13 22:59:47.108386	23	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
3	2bffcaa0-aaf2-11e3-a122-2d3cb1fb0bbd	2014-03-13 20:58:10.851521	2014-03-13 20:59:22.0553	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
26	85449446-ab02-11e3-a326-2d3cb1fb0bbd	2014-03-13 22:55:11.412656	2014-03-13 22:59:47.731724	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
4	2c759e54-aaf4-11e3-a135-2d3cb1fb0bbd	2014-03-13 21:12:28.937092	2014-03-13 21:12:47.049194	23	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
53	8cacdc6c-ab4c-11e3-a56c-2d3cb1fb0bbd	2014-03-14 07:45:05.690416	2014-03-14 07:45:31.017438	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
5	401ee88e-aaf4-11e3-a148-2d3cb1fb0bbd	2014-03-13 21:13:01.120983	2014-03-13 21:13:17.35131	24	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
6	93515c1c-aaf4-11e3-a180-2d3cb1fb0bbd	\N	2014-03-13 21:16:25.613457	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
7	a3e1564a-aaf4-11e3-a192-2d3cb1fb0bbd	\N	2014-03-13 21:16:53.480787	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
8	dd8c6c18-aaf4-11e3-a1b6-2d3cb1fb0bbd	\N	2014-03-13 21:17:35.965574	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
9	17bde772-aaf5-11e3-a1de-2d3cb1fb0bbd	\N	2014-03-13 21:20:07.737324	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
10	4cb63510-aaf5-11e3-a1f1-2d3cb1fb0bbd	2014-03-13 21:20:32.222293	2014-03-13 21:21:14.962334	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
31	13cf3602-ab04-11e3-a386-2d3cb1fb0bbd	2014-03-13 23:06:19.126658	2014-03-13 23:07:23.092046	23	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
11	277841ca-aaf6-11e3-a204-2d3cb1fb0bbd	2014-03-13 21:26:39.89978	2014-03-13 21:27:03.039175	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
30	12f34f0c-ab04-11e3-a382-2d3cb1fb0bbd	2014-03-13 23:06:17.942937	2014-03-13 23:07:29.689733	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
12	3c539810-aaf6-11e3-a217-2d3cb1fb0bbd	2014-03-13 21:27:13.585843	2014-03-13 21:27:17.000173	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
13	091f025e-aafb-11e3-a21d-2d3cb1fb0bbd	2014-03-13 22:01:49.707472	2014-03-13 22:01:51.233525	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
14	19232234-aafb-11e3-a221-2d3cb1fb0bbd	2014-03-13 22:02:04.180404	2014-03-13 22:03:36.412486	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
15	83374178-aafb-11e3-a234-2d3cb1fb0bbd	2014-03-13 22:05:01.048178	2014-03-13 22:09:40.649841	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
46	e4c01b60-ab08-11e3-a4e0-2d3cb1fb0bbd	2014-03-13 23:40:47.824968	2014-03-13 23:41:15.25971	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
17	820169da-aafd-11e3-a25e-2d3cb1fb0bbd	\N	2014-03-13 22:19:19.643254	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
16	784c1ff2-aafd-11e3-a247-2d3cb1fb0bbd	2014-03-13 22:19:01.341655	2014-03-13 22:20:50.268401	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
34	6978adbc-ab05-11e3-a3cd-2d3cb1fb0bbd	\N	2014-03-13 23:15:54.376485	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
19	db7f5ce2-aafd-11e3-a2a4-2d3cb1fb0bbd	\N	2014-03-13 22:21:49.741522	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
18	c71cf44e-aafd-11e3-a27f-2d3cb1fb0bbd	2014-03-13 22:21:14.03332	2014-03-13 22:22:13.023462	21	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
33	65f86a9c-ab05-11e3-a3bc-2d3cb1fb0bbd	2014-03-13 23:15:46.501268	2014-03-13 23:15:57.808677	23	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
20	f208cc32-aafd-11e3-a2b6-2d3cb1fb0bbd	2014-03-13 22:22:25.682456	2014-03-13 22:23:47.781609	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
32	e83cf7c6-ab04-11e3-a3a5-2d3cb1fb0bbd	2014-03-13 23:12:17.211889	2014-03-13 23:16:04.378426	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
22	37ff98b8-ab00-11e3-a2cd-2d3cb1fb0bbd	2014-03-13 22:38:42.236726	2014-03-13 22:39:03.93274	23	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
21	33c5aeb8-ab00-11e3-a2c9-2d3cb1fb0bbd	2014-03-13 22:38:35.640924	2014-03-13 22:39:04.133226	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
45	e4c11b78-ab08-11e3-a4e4-2d3cb1fb0bbd	2014-03-13 23:40:47.691468	2014-03-13 23:41:15.279132	23	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
23	86bad954-ab00-11e3-a2ee-2d3cb1fb0bbd	2014-03-13 22:40:53.944743	2014-03-13 22:41:30.723061	23	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
24	92f33e28-ab00-11e3-a301-2d3cb1fb0bbd	2014-03-13 22:41:14.647866	2014-03-13 22:41:38.375561	21	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
25	22c0daf6-ab01-11e3-a313-2d3cb1fb0bbd	2014-03-13 22:45:15.671794	2014-03-13 22:45:22.882913	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
37	fcb098b4-ab06-11e3-a441-2d3cb1fb0bbd	\N	2014-03-13 23:27:05.862609	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
325	c19795ea-b923-11e3-9120-2d3cb1fb0bbd	2014-03-31 22:28:24.670437	\N	55	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
35	85735c7e-ab05-11e3-a3eb-2d3cb1fb0bbd	2014-03-13 23:16:40.433939	2014-03-13 23:35:32.489517	23	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
39	27c0bb0a-ab08-11e3-a474-2d3cb1fb0bbd	\N	2014-03-13 23:35:32.65451	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
40	27dd3532-ab08-11e3-a478-2d3cb1fb0bbd	\N	2014-03-13 23:35:32.796816	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
36	880d7e6a-ab05-11e3-a3ef-2d3cb1fb0bbd	2014-03-13 23:16:44.1319	2014-03-13 23:35:39.022838	21	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
47	fc55c248-ab08-11e3-a504-2d3cb1fb0bbd	2014-03-13 23:41:27.029761	2014-03-13 23:41:45.173328	23	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
42	4196b458-ab08-11e3-a496-2d3cb1fb0bbd	2014-03-13 23:36:14.410524	2014-03-13 23:37:08.421568	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
41	4198496c-ab08-11e3-a49a-2d3cb1fb0bbd	2014-03-13 23:36:14.129212	2014-03-13 23:37:14.863978	23	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
48	fc564a38-ab08-11e3-a508-2d3cb1fb0bbd	2014-03-13 23:41:27.391349	2014-03-13 23:41:55.217281	21	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
44	a15288a4-ab08-11e3-a4bb-2d3cb1fb0bbd	2014-03-13 23:38:56.010844	2014-03-13 23:39:35.499507	23	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
43	a153d5ec-ab08-11e3-a4bf-2d3cb1fb0bbd	2014-03-13 23:38:54.782255	2014-03-13 23:39:36.197102	21	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
59	3c45861c-b104-11e3-b093-2d3cb1fb0bbd	2014-03-21 14:22:32.388183	2014-03-21 14:22:32.993833	27	28	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
56	c6c00db6-ab4c-11e3-a594-2d3cb1fb0bbd	2014-03-14 07:46:44.108579	2014-03-14 07:46:54.7839	21	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
50	9a2da25a-ab4b-11e3-a53b-2d3cb1fb0bbd	2014-03-14 07:38:22.267533	2014-03-14 07:38:42.824542	23	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
49	9a2da2b4-ab4b-11e3-a53c-2d3cb1fb0bbd	2014-03-14 07:38:19.969151	2014-03-14 07:38:51.847049	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
55	c6bf173a-ab4c-11e3-a590-2d3cb1fb0bbd	2014-03-14 07:46:43.245789	2014-03-14 07:46:56.575638	23	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
52	7da5ebf0-ab4c-11e3-a560-2d3cb1fb0bbd	\N	2014-03-14 07:44:44.732653	\N	\N	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
51	7da6f2e8-ab4c-11e3-a564-2d3cb1fb0bbd	2014-03-14 07:44:40.586196	2014-03-14 07:44:44.74067	21	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
54	8cafcae4-ab4c-11e3-a570-2d3cb1fb0bbd	2014-03-14 07:45:05.952237	2014-03-14 07:45:20.62574	23	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
57	d870b786-ab4c-11e3-a5b8-2d3cb1fb0bbd	2014-03-14 07:47:13.116331	2014-03-14 07:47:28.050322	23	26	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
58	d86d28e6-ab4c-11e3-a5b4-2d3cb1fb0bbd	2014-03-14 07:47:13.307425	2014-03-14 07:52:59.91619	21	22	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
60	e5873152-b281-11e3-b157-2d3cb1fb0bbd	2014-03-23 11:54:33.130941	2014-03-23 11:54:33.235718	27	29	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
62	eab030ac-b281-11e3-b167-2d3cb1fb0bbd	2014-03-23 11:54:41.29858	2014-03-23 11:54:41.38055	27	31	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
65	f1ecec0c-b281-11e3-b17f-2d3cb1fb0bbd	2014-03-23 11:54:53.263671	2014-03-23 11:54:53.33864	27	34	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
61	e87c03b0-b281-11e3-b15f-2d3cb1fb0bbd	2014-03-23 11:54:37.58771	2014-03-23 11:54:37.642584	27	30	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
64	ef870f60-b281-11e3-b177-2d3cb1fb0bbd	2014-03-23 11:54:49.497245	2014-03-23 11:54:49.5797	27	33	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
63	ed3ad4b2-b281-11e3-b16f-2d3cb1fb0bbd	2014-03-23 11:54:45.422363	2014-03-23 11:54:45.480555	27	32	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
66	f4560618-b281-11e3-b187-2d3cb1fb0bbd	2014-03-23 11:54:57.326176	2014-03-23 11:54:57.407316	27	35	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
67	86c06802-b47d-11e3-b66e-2d3cb1fb0bbd	2014-03-26 00:28:17.806552	2014-03-26 00:28:17.907468	27	36	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
68	88bd22a8-b47d-11e3-b676-2d3cb1fb0bbd	2014-03-26 00:28:21.046572	2014-03-26 00:28:21.18857	27	37	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
69	8a306b4a-b47d-11e3-b67e-2d3cb1fb0bbd	2014-03-26 00:28:23.635666	2014-03-26 00:28:23.751715	27	31	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
70	8c16c59e-b47d-11e3-b686-2d3cb1fb0bbd	2014-03-26 00:28:26.767254	2014-03-26 00:28:26.858078	27	30	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
71	8e0228d0-b47d-11e3-b68e-2d3cb1fb0bbd	2014-03-26 00:28:29.906452	2014-03-26 00:28:30.52492	27	29	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
72	8fb91198-b47d-11e3-b696-2d3cb1fb0bbd	2014-03-26 00:28:32.820926	2014-03-26 00:28:32.890152	27	38	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
73	913494ac-b47d-11e3-b69e-2d3cb1fb0bbd	2014-03-26 00:28:35.249487	2014-03-26 00:28:35.321432	27	39	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
74	93a0ed76-b47d-11e3-b6a6-2d3cb1fb0bbd	2014-03-26 00:28:39.556886	2014-03-26 00:28:39.623869	27	40	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
93	dc89bf06-b755-11e3-82fe-2d3cb1fb0bbd	2014-03-29 15:21:55.75888	2014-03-29 15:21:55.870024	55	60	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
75	db8d41f4-b679-11e3-813e-2d3cb1fb0bbd	2014-03-28 13:07:05.032099	2014-03-28 13:07:05.659105	27	41	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
76	e6f9d05c-b679-11e3-8151-2d3cb1fb0bbd	2014-03-28 13:07:23.527892	2014-03-28 13:07:23.592903	27	42	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
107	c892d798-b922-11e3-85e2-2d3cb1fb0bbd	2014-03-31 22:21:20.17535	2014-03-31 22:21:20.243015	27	73	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
94	88229180-b922-11e3-8559-2d3cb1fb0bbd	2014-03-31 22:19:32.573263	2014-03-31 22:19:32.697668	27	61	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
77	eb49a7ae-b679-11e3-8159-2d3cb1fb0bbd	2014-03-28 13:07:30.812817	2014-03-28 13:07:30.886339	27	43	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
78	efdc4c9a-b679-11e3-8161-2d3cb1fb0bbd	2014-03-28 13:07:39.273369	2014-03-28 13:07:39.348148	27	44	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
95	989fe62a-b922-11e3-8577-2d3cb1fb0bbd	2014-03-31 22:19:59.625373	2014-03-31 22:19:59.706732	27	62	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
79	f996ca62-b679-11e3-8174-2d3cb1fb0bbd	2014-03-28 13:07:54.794593	2014-03-28 13:07:54.859348	27	45	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
117	6f430388-b923-11e3-870f-2d3cb1fb0bbd	2014-03-31 22:26:00.458971	2014-03-31 22:26:00.527791	27	82	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
80	fcd0cb88-b679-11e3-817c-2d3cb1fb0bbd	2014-03-28 13:08:00.170432	2014-03-28 13:08:00.264515	27	46	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
108	d2ca9bc4-b922-11e3-85ea-2d3cb1fb0bbd	2014-03-31 22:21:37.210744	2014-03-31 22:21:37.266533	27	74	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
96	9cf7600e-b922-11e3-857f-2d3cb1fb0bbd	2014-03-31 22:20:07.401511	2014-03-31 22:20:07.483897	27	63	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
81	0024defa-b67a-11e3-8184-2d3cb1fb0bbd	2014-03-28 13:08:05.795811	2014-03-28 13:08:06.455556	27	47	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
82	0405eabe-b67a-11e3-818c-2d3cb1fb0bbd	2014-03-28 13:08:12.38443	2014-03-28 13:08:12.463838	27	48	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
97	a29a9c60-b922-11e3-8587-2d3cb1fb0bbd	2014-03-31 22:20:16.351845	2014-03-31 22:20:16.429487	27	64	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
83	0b783cd4-b67a-11e3-819f-2d3cb1fb0bbd	2014-03-28 13:08:24.754071	2014-03-28 13:08:24.84226	27	49	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
109	d4b79d88-b922-11e3-85f2-2d3cb1fb0bbd	2014-03-31 22:21:40.427394	2014-03-31 22:21:40.482518	27	61	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
84	5847698c-b750-11e3-8296-2d3cb1fb0bbd	2014-03-29 14:42:26.028721	2014-03-29 14:42:26.103357	27	50	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
98	a5d3a084-b922-11e3-858f-2d3cb1fb0bbd	2014-03-31 22:20:21.761768	2014-03-31 22:20:21.837012	27	65	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
85	59507fe4-b750-11e3-829e-2d3cb1fb0bbd	2014-03-29 14:42:28.459662	2014-03-29 14:42:28.537536	27	51	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
134	748fbce6-b923-11e3-8807-2d3cb1fb0bbd	2014-03-31 22:26:09.495229	2014-03-31 22:26:09.555203	27	99	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
86	5b4082b8-b750-11e3-82a6-2d3cb1fb0bbd	2014-03-29 14:42:31.829365	2014-03-29 14:42:31.871625	27	52	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
99	a8700f9e-b922-11e3-8597-2d3cb1fb0bbd	2014-03-31 22:20:26.139584	2014-03-31 22:20:26.19784	27	66	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
87	5db7902c-b750-11e3-82b0-2d3cb1fb0bbd	2014-03-29 14:42:35.966846	2014-03-29 14:42:36.031047	27	53	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
110	202a574c-b923-11e3-8629-2d3cb1fb0bbd	2014-03-31 22:23:47.012817	2014-03-31 22:23:47.100061	27	75	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
88	5f0b0760-b750-11e3-82ba-2d3cb1fb0bbd	2014-03-29 14:42:37.428238	2014-03-29 14:42:37.519633	27	54	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
100	b11a8214-b922-11e3-85aa-2d3cb1fb0bbd	2014-03-31 22:20:41.181729	2014-03-31 22:20:41.590609	27	62	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
89	d8cbffa0-b755-11e3-82d2-2d3cb1fb0bbd	2014-03-29 15:21:49.319913	2014-03-29 15:21:49.419556	55	56	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
118	6f383f7a-b923-11e3-870a-2d3cb1fb0bbd	2014-03-31 22:26:01.429612	2014-03-31 22:26:01.555679	27	83	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
101	b369610c-b922-11e3-85b2-2d3cb1fb0bbd	2014-03-31 22:20:44.554351	2014-03-31 22:20:44.626249	27	67	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
90	dac42dfa-b755-11e3-82e6-2d3cb1fb0bbd	2014-03-29 15:21:52.444468	2014-03-29 15:21:52.538366	55	57	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
91	db1f2962-b755-11e3-82ee-2d3cb1fb0bbd	2014-03-29 15:21:53.082934	2014-03-29 15:21:53.182395	55	58	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
111	262ab916-b923-11e3-8631-2d3cb1fb0bbd	2014-03-31 22:23:57.080041	2014-03-31 22:23:57.249926	27	76	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
102	b5786876-b922-11e3-85ba-2d3cb1fb0bbd	2014-03-31 22:20:48.507436	2014-03-31 22:20:48.565183	27	68	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
92	dbc3f352-b755-11e3-82f6-2d3cb1fb0bbd	2014-03-29 15:21:53.95873	2014-03-29 15:21:54.006677	55	59	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
128	6f1fc800-b923-11e3-8700-2d3cb1fb0bbd	2014-03-31 22:26:07.516056	2014-03-31 22:26:07.820413	27	93	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
129	6f29d6e2-b923-11e3-8704-2d3cb1fb0bbd	2014-03-31 22:26:07.788469	2014-03-31 22:26:07.862138	27	94	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
103	b7c735da-b922-11e3-85c2-2d3cb1fb0bbd	2014-03-31 22:20:51.877663	2014-03-31 22:20:51.943105	27	69	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
112	28ad99ec-b923-11e3-8639-2d3cb1fb0bbd	2014-03-31 22:24:01.295364	2014-03-31 22:24:01.372193	27	77	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
104	bbc99ff6-b922-11e3-85ca-2d3cb1fb0bbd	2014-03-31 22:20:59.118103	2014-03-31 22:20:59.177617	27	70	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
119	6fe968ea-b923-11e3-8727-2d3cb1fb0bbd	2014-03-31 22:26:01.582477	2014-03-31 22:26:01.656837	27	84	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
105	be4522a0-b922-11e3-85d2-2d3cb1fb0bbd	2014-03-31 22:21:03.290061	2014-03-31 22:21:03.359569	27	71	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
113	4c69a344-b923-11e3-8699-2d3cb1fb0bbd	2014-03-31 22:25:03.116073	2014-03-31 22:25:03.170891	27	78	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
106	c1c0c9de-b922-11e3-85da-2d3cb1fb0bbd	2014-03-31 22:21:08.731872	2014-03-31 22:21:08.788021	27	72	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
124	7242a354-b923-11e3-8798-2d3cb1fb0bbd	2014-03-31 22:26:05.68061	2014-03-31 22:26:05.756023	27	89	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
125	6f25140e-b923-11e3-8702-2d3cb1fb0bbd	2014-03-31 22:26:05.726768	2014-03-31 22:26:05.806691	27	90	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
120	6ea2a21c-b923-11e3-86d0-2d3cb1fb0bbd	2014-03-31 22:26:02.688721	2014-03-31 22:26:02.764339	27	85	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
114	53e1f9b4-b923-11e3-86a1-2d3cb1fb0bbd	2014-03-31 22:25:13.807309	2014-03-31 22:25:13.877121	27	79	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
115	6e8f6e0e-b923-11e3-86c8-2d3cb1fb0bbd	2014-03-31 22:25:58.635425	2014-03-31 22:25:58.716128	27	80	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
121	707bbf60-b923-11e3-8733-2d3cb1fb0bbd	2014-03-31 22:26:03.613335	2014-03-31 22:26:03.671266	27	86	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
116	6f1b0086-b923-11e3-86fe-2d3cb1fb0bbd	2014-03-31 22:25:59.971395	2014-03-31 22:26:00.063917	27	81	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
132	723455ec-b923-11e3-8792-2d3cb1fb0bbd	2014-03-31 22:26:09.165925	2014-03-31 22:26:09.232663	27	97	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
122	71388474-b923-11e3-874d-2d3cb1fb0bbd	2014-03-31 22:26:03.679582	2014-03-31 22:26:03.752614	27	87	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
130	6fc57ae8-b923-11e3-871b-2d3cb1fb0bbd	2014-03-31 22:26:08.094813	2014-03-31 22:26:08.164726	27	95	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
123	7135eebc-b923-11e3-874c-2d3cb1fb0bbd	2014-03-31 22:26:04.647236	2014-03-31 22:26:04.71906	27	88	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
126	72e96f68-b923-11e3-87b4-2d3cb1fb0bbd	2014-03-31 22:26:07.273434	2014-03-31 22:26:07.427057	27	91	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
127	72643276-b923-11e3-87a6-2d3cb1fb0bbd	2014-03-31 22:26:07.388999	2014-03-31 22:26:07.459728	27	92	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
136	741e669a-b923-11e3-87f1-2d3cb1fb0bbd	2014-03-31 22:26:10.18922	2014-03-31 22:26:10.24034	27	86	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
133	724842dc-b923-11e3-879a-2d3cb1fb0bbd	2014-03-31 22:26:09.256084	2014-03-31 22:26:09.313164	27	98	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
131	723dd0ea-b923-11e3-8796-2d3cb1fb0bbd	2014-03-31 22:26:08.709124	2014-03-31 22:26:08.768369	27	96	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
135	7077029a-b923-11e3-8731-2d3cb1fb0bbd	2014-03-31 22:26:09.563013	2014-03-31 22:26:09.636324	27	100	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
137	75c64a30-b923-11e3-8843-2d3cb1fb0bbd	2014-03-31 22:26:11.141093	2014-03-31 22:26:11.188846	27	97	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
139	754b047e-b923-11e3-882d-2d3cb1fb0bbd	2014-03-31 22:26:11.650971	2014-03-31 22:26:11.716318	27	102	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
138	753c938a-b923-11e3-8827-2d3cb1fb0bbd	2014-03-31 22:26:11.240821	2014-03-31 22:26:11.290377	27	101	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
140	741e7bc6-b923-11e3-87f2-2d3cb1fb0bbd	2014-03-31 22:26:11.777054	2014-03-31 22:26:11.835943	27	85	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
142	768dfcd8-b923-11e3-887a-2d3cb1fb0bbd	2014-03-31 22:26:12.735752	2014-03-31 22:26:12.784279	27	104	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
141	767acff0-b923-11e3-8873-2d3cb1fb0bbd	2014-03-31 22:26:12.68527	2014-03-31 22:26:12.769401	27	103	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
143	77f3201c-b923-11e3-88be-2d3cb1fb0bbd	2014-03-31 22:26:13.904663	2014-03-31 22:26:13.954527	27	105	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
144	75cfedc4-b923-11e3-8847-2d3cb1fb0bbd	2014-03-31 22:26:14.213354	2014-03-31 22:26:14.260105	27	96	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
145	77c9c438-b923-11e3-88b6-2d3cb1fb0bbd	2014-03-31 22:26:14.861109	2014-03-31 22:26:14.925971	27	106	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
146	788f8d4e-b923-11e3-88de-2d3cb1fb0bbd	2014-03-31 22:26:14.935422	2014-03-31 22:26:15.033363	27	107	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
147	7898ef42-b923-11e3-88e5-2d3cb1fb0bbd	2014-03-31 22:26:14.995466	2014-03-31 22:26:15.0685	27	108	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
166	7b697b24-b923-11e3-897e-2d3cb1fb0bbd	2014-03-31 22:26:23.951235	2014-03-31 22:26:24.011122	27	126	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
148	77c010a0-b923-11e3-88b2-2d3cb1fb0bbd	2014-03-31 22:26:15.782361	2014-03-31 22:26:15.856116	27	109	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
196	83c6ff80-b923-11e3-8b68-2d3cb1fb0bbd	2014-03-31 22:26:35.920254	2014-03-31 22:26:35.991011	27	153	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
189	81fa051c-b923-11e3-8b04-2d3cb1fb0bbd	2014-03-31 22:26:32.855983	2014-03-31 22:26:32.920975	27	148	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
167	797a8f42-b923-11e3-8914-2d3cb1fb0bbd	2014-03-31 22:26:24.385571	2014-03-31 22:26:24.454282	27	127	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
149	77d34148-b923-11e3-88ba-2d3cb1fb0bbd	2014-03-31 22:26:15.863858	2014-03-31 22:26:15.93867	27	110	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
150	7924274c-b923-11e3-890a-2d3cb1fb0bbd	2014-03-31 22:26:15.908078	2014-03-31 22:26:15.979129	27	111	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
179	7cbaa138-b923-11e3-89ed-2d3cb1fb0bbd	2014-03-31 22:26:29.969361	2014-03-31 22:26:30.046261	27	139	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
151	79a14664-b923-11e3-891a-2d3cb1fb0bbd	2014-03-31 22:26:16.723745	2014-03-31 22:26:16.764679	27	112	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
180	818cdcf8-b923-11e3-8af1-2d3cb1fb0bbd	2014-03-31 22:26:30.013601	2014-03-31 22:26:30.086715	27	140	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
168	7c176072-b923-11e3-89b2-2d3cb1fb0bbd	2014-03-31 22:26:24.770169	2014-03-31 22:26:24.859833	27	128	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
152	77adef42-b923-11e3-88aa-2d3cb1fb0bbd	2014-03-31 22:26:17.672302	2014-03-31 22:26:17.760767	27	113	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
153	78f25b4a-b923-11e3-88f5-2d3cb1fb0bbd	2014-03-31 22:26:17.727058	2014-03-31 22:26:17.79244	27	114	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
169	7a117196-b923-11e3-8925-2d3cb1fb0bbd	2014-03-31 22:26:25.363091	2014-03-31 22:26:25.422026	27	129	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
154	782d598a-b923-11e3-88cb-2d3cb1fb0bbd	2014-03-31 22:26:18.181689	2014-03-31 22:26:18.255276	27	115	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
155	75dbeaf2-b923-11e3-884b-2d3cb1fb0bbd	2014-03-31 22:26:18.905453	2014-03-31 22:26:18.944085	27	98	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
181	81cc45c8-b923-11e3-8afb-2d3cb1fb0bbd	2014-03-31 22:26:30.428725	2014-03-31 22:26:30.510613	27	141	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
156	798444e2-b923-11e3-8918-2d3cb1fb0bbd	2014-03-31 22:26:18.961785	2014-03-31 22:26:19.022537	27	116	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
170	7a255878-b923-11e3-892b-2d3cb1fb0bbd	2014-03-31 22:26:25.819961	2014-03-31 22:26:25.867693	27	130	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
157	7b29c60a-b923-11e3-896b-2d3cb1fb0bbd	2014-03-31 22:26:19.30055	2014-03-31 22:26:19.365866	27	117	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
190	835f25fe-b923-11e3-8b53-2d3cb1fb0bbd	2014-03-31 22:26:33.06791	2014-03-31 22:26:33.122648	27	140	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
171	7c9b5940-b923-11e3-89e1-2d3cb1fb0bbd	2014-03-31 22:26:25.950622	2014-03-31 22:26:26.00916	27	131	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
182	8211172a-b923-11e3-8b0c-2d3cb1fb0bbd	2014-03-31 22:26:30.881254	2014-03-31 22:26:30.938532	27	142	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
172	7f5d94e0-b923-11e3-8a70-2d3cb1fb0bbd	2014-03-31 22:26:26.346686	2014-03-31 22:26:26.391054	27	132	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
158	7ab43052-b923-11e3-8949-2d3cb1fb0bbd	2014-03-31 22:26:19.811954	2014-03-31 22:26:20.918354	27	118	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
159	7ac7818e-b923-11e3-8951-2d3cb1fb0bbd	2014-03-31 22:26:20.823506	2014-03-31 22:26:20.925441	27	119	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
160	767614f6-b923-11e3-8871-2d3cb1fb0bbd	2014-03-31 22:26:20.856577	2014-03-31 22:26:20.940696	27	120	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
161	7722b076-b923-11e3-889a-2d3cb1fb0bbd	2014-03-31 22:26:20.886579	2014-03-31 22:26:20.947408	27	121	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
206	8736439c-b923-11e3-8bf5-2d3cb1fb0bbd	2014-03-31 22:26:39.513739	2014-03-31 22:26:39.587076	27	163	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
204	866497f2-b923-11e3-8bda-2d3cb1fb0bbd	2014-03-31 22:26:38.139676	2014-03-31 22:26:38.212419	27	161	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
162	7b519504-b923-11e3-8974-2d3cb1fb0bbd	2014-03-31 22:26:21.369328	2014-03-31 22:26:21.44699	27	122	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
163	771d8664-b923-11e3-8898-2d3cb1fb0bbd	2014-03-31 22:26:21.404624	2014-03-31 22:26:21.46702	27	123	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
183	8224c496-b923-11e3-8b13-2d3cb1fb0bbd	2014-03-31 22:26:31.009501	2014-03-31 22:26:31.081044	27	143	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
173	7abdcf22-b923-11e3-894d-2d3cb1fb0bbd	2014-03-31 22:26:26.80311	2014-03-31 22:26:26.878867	27	133	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
164	7a16310e-b923-11e3-8927-2d3cb1fb0bbd	2014-03-31 22:26:22.393492	2014-03-31 22:26:22.435893	27	124	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
174	7ad10ccc-b923-11e3-8955-2d3cb1fb0bbd	2014-03-31 22:26:26.846556	2014-03-31 22:26:26.916972	27	134	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
165	7b563dd4-b923-11e3-8976-2d3cb1fb0bbd	2014-03-31 22:26:23.848375	2014-03-31 22:26:23.912317	27	125	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
191	7edfb85e-b923-11e3-8a52-2d3cb1fb0bbd	2014-03-31 22:26:33.411813	2014-03-31 22:26:33.465919	27	149	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
175	7dc572e2-b923-11e3-8a1b-2d3cb1fb0bbd	2014-03-31 22:26:27.829561	2014-03-31 22:26:27.949614	27	135	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
184	82719b68-b923-11e3-8b1a-2d3cb1fb0bbd	2014-03-31 22:26:31.512601	2014-03-31 22:26:31.584705	27	144	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
176	80156c5a-b923-11e3-8a9f-2d3cb1fb0bbd	2014-03-31 22:26:28.918378	2014-03-31 22:26:28.97535	27	136	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
197	852aa782-b923-11e3-8ba0-2d3cb1fb0bbd	2014-03-31 22:26:36.081809	2014-03-31 22:26:36.17265	27	154	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
177	7e61df1a-b923-11e3-8a3e-2d3cb1fb0bbd	2014-03-31 22:26:28.995128	2014-03-31 22:26:29.075493	27	137	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
185	82cad4da-b923-11e3-8b2b-2d3cb1fb0bbd	2014-03-31 22:26:32.097248	2014-03-31 22:26:32.15228	27	83	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
178	8028827c-b923-11e3-8aa7-2d3cb1fb0bbd	2014-03-31 22:26:29.824995	2014-03-31 22:26:29.882845	27	138	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
192	842818c4-b923-11e3-8b72-2d3cb1fb0bbd	2014-03-31 22:26:34.384276	2014-03-31 22:26:34.432945	27	150	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
186	82d3fc5e-b923-11e3-8b31-2d3cb1fb0bbd	2014-03-31 22:26:32.160547	2014-03-31 22:26:32.21247	27	145	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
201	85ef5474-b923-11e3-8bbc-2d3cb1fb0bbd	2014-03-31 22:26:37.378111	2014-03-31 22:26:37.423361	27	158	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
193	8487597e-b923-11e3-8b82-2d3cb1fb0bbd	2014-03-31 22:26:35.012973	2014-03-31 22:26:35.058451	27	83	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
187	82ebac1e-b923-11e3-8b39-2d3cb1fb0bbd	2014-03-31 22:26:32.311526	2014-03-31 22:26:32.375315	27	146	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
188	82fb1f78-b923-11e3-8b40-2d3cb1fb0bbd	2014-03-31 22:26:32.41519	2014-03-31 22:26:32.475714	27	147	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
198	8548f67e-b923-11e3-8ba7-2d3cb1fb0bbd	2014-03-31 22:26:36.277818	2014-03-31 22:26:36.353873	27	155	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
194	84a687fe-b923-11e3-8b89-2d3cb1fb0bbd	2014-03-31 22:26:35.24046	2014-03-31 22:26:35.301802	27	151	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
195	84bb70c4-b923-11e3-8b90-2d3cb1fb0bbd	2014-03-31 22:26:35.352549	2014-03-31 22:26:35.424706	27	152	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
202	8601b858-b923-11e3-8bc3-2d3cb1fb0bbd	2014-03-31 22:26:37.487842	2014-03-31 22:26:37.526522	27	159	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
199	855d5e34-b923-11e3-8bae-2d3cb1fb0bbd	2014-03-31 22:26:36.411563	2014-03-31 22:26:36.477134	27	156	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
209	87c852f0-b923-11e3-8c13-2d3cb1fb0bbd	2014-03-31 22:26:40.466893	2014-03-31 22:26:40.555723	27	166	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
200	85c99450-b923-11e3-8bb5-2d3cb1fb0bbd	2014-03-31 22:26:37.119979	2014-03-31 22:26:37.160845	27	157	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
205	868496e2-b923-11e3-8be2-2d3cb1fb0bbd	2014-03-31 22:26:38.345886	2014-03-31 22:26:38.393761	27	162	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
203	83d0a1de-b923-11e3-8b6c-2d3cb1fb0bbd	2014-03-31 22:26:38.067032	2014-03-31 22:26:38.131338	27	160	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
208	86e31848-b923-11e3-8bef-2d3cb1fb0bbd	2014-03-31 22:26:40.050815	2014-03-31 22:26:40.11414	27	165	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
207	87473bfc-b923-11e3-8bfc-2d3cb1fb0bbd	2014-03-31 22:26:39.62382	2014-03-31 22:26:39.688984	27	164	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
210	87654cc8-b923-11e3-8c03-2d3cb1fb0bbd	2014-03-31 22:26:41.024934	2014-03-31 22:26:41.101298	27	167	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
211	883685cc-b923-11e3-8c28-2d3cb1fb0bbd	2014-03-31 22:26:41.189885	2014-03-31 22:26:41.242038	27	168	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
212	8864063c-b923-11e3-8c2f-2d3cb1fb0bbd	2014-03-31 22:26:41.487986	2014-03-31 22:26:41.523685	27	169	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
213	88afdb52-b923-11e3-8c3c-2d3cb1fb0bbd	2014-03-31 22:26:41.98549	2014-03-31 22:26:42.029144	27	170	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
214	88b8ee04-b923-11e3-8c42-2d3cb1fb0bbd	2014-03-31 22:26:42.059708	2014-03-31 22:26:42.129912	27	171	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
215	890ea15a-b923-11e3-8c4a-2d3cb1fb0bbd	2014-03-31 22:26:42.605493	2014-03-31 22:26:42.653097	27	172	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
216	86de49d0-b923-11e3-8bed-2d3cb1fb0bbd	2014-03-31 22:26:43.149159	2014-03-31 22:26:43.219284	27	173	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
217	8998806e-b923-11e3-8c65-2d3cb1fb0bbd	2014-03-31 22:26:43.524163	2014-03-31 22:26:43.58108	27	174	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
218	89f39620-b923-11e3-8c6e-2d3cb1fb0bbd	2014-03-31 22:26:44.10955	2014-03-31 22:26:44.188771	27	175	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
251	9702f216-b923-11e3-8d78-2d3cb1fb0bbd	2014-03-31 22:27:06.016313	2014-03-31 22:27:06.070313	27	206	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
219	8a033aa8-b923-11e3-8c75-2d3cb1fb0bbd	2014-03-31 22:26:44.211364	2014-03-31 22:26:44.268899	27	176	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
238	9053efba-b923-11e3-8d1d-2d3cb1fb0bbd	2014-03-31 22:26:54.8044	2014-03-31 22:26:54.843698	27	194	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
220	8a1c7e64-b923-11e3-8c7c-2d3cb1fb0bbd	2014-03-31 22:26:44.383572	2014-03-31 22:26:44.450286	27	177	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
260	b27d523e-b923-11e3-8dde-2d3cb1fb0bbd	2014-03-31 22:27:53.24599	2014-03-31 22:27:53.334539	55	214	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
221	892eef5a-b923-11e3-8c51-2d3cb1fb0bbd	2014-03-31 22:26:45.088337	2014-03-31 22:26:45.154884	27	178	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
261	b2956108-b923-11e3-8de8-2d3cb1fb0bbd	2014-03-31 22:27:53.30205	2014-03-31 22:27:53.362952	55	215	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
239	90d42a72-b923-11e3-8d24-2d3cb1fb0bbd	2014-03-31 22:26:55.645554	2014-03-31 22:26:55.711561	27	195	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
222	8acf7686-b923-11e3-8c95-2d3cb1fb0bbd	2014-03-31 22:26:45.549048	2014-03-31 22:26:45.597484	27	179	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
223	8a7abd8a-b923-11e3-8c8b-2d3cb1fb0bbd	2014-03-31 22:26:46.138023	2014-03-31 22:26:46.181305	27	180	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
240	9168b2b4-b923-11e3-8d2b-2d3cb1fb0bbd	2014-03-31 22:26:56.618943	2014-03-31 22:26:56.696003	27	196	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
224	8c9c36d4-b923-11e3-8cbb-2d3cb1fb0bbd	2014-03-31 22:26:48.571451	2014-03-31 22:26:48.635633	27	181	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
272	b5ac7f02-b923-11e3-8e80-2d3cb1fb0bbd	2014-03-31 22:27:58.401449	2014-03-31 22:27:58.438267	55	226	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
225	8d3799bc-b923-11e3-8cc4-2d3cb1fb0bbd	2014-03-31 22:26:49.585997	2014-03-31 22:26:49.681755	27	182	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
252	977527c8-b923-11e3-8d80-2d3cb1fb0bbd	2014-03-31 22:27:06.766918	2014-03-31 22:27:06.897091	27	207	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
241	9188cefa-b923-11e3-8d32-2d3cb1fb0bbd	2014-03-31 22:26:56.828617	2014-03-31 22:26:56.87746	27	197	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
226	8d4a4e5e-b923-11e3-8ccb-2d3cb1fb0bbd	2014-03-31 22:26:49.725091	2014-03-31 22:26:49.762662	27	183	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
227	8d8b503e-b923-11e3-8cd2-2d3cb1fb0bbd	2014-03-31 22:26:50.134741	2014-03-31 22:26:50.186502	27	154	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
253	977f06bc-b923-11e3-8d86-2d3cb1fb0bbd	2014-03-31 22:27:06.831555	2014-03-31 22:27:06.903634	27	208	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
228	8dcd87e2-b923-11e3-8cd9-2d3cb1fb0bbd	2014-03-31 22:26:50.567665	2014-03-31 22:26:50.610034	27	184	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
242	92f34432-b923-11e3-8d39-2d3cb1fb0bbd	2014-03-31 22:26:59.205223	2014-03-31 22:26:59.270707	27	198	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
229	8ddb6af6-b923-11e3-8ce0-2d3cb1fb0bbd	2014-03-31 22:26:50.658846	2014-03-31 22:26:50.73121	27	185	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
267	b3afe89c-b923-11e3-8e1e-2d3cb1fb0bbd	2014-03-31 22:27:56.137199	2014-03-31 22:27:56.233754	55	221	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
254	b1c27040-b923-11e3-8d95-2d3cb1fb0bbd	2014-03-31 22:27:51.355925	2014-03-31 22:27:51.409997	55	73	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
230	8e1f9c9e-b923-11e3-8ce7-2d3cb1fb0bbd	2014-03-31 22:26:51.108058	2014-03-31 22:26:51.17699	27	186	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
243	9304692e-b923-11e3-8d40-2d3cb1fb0bbd	2014-03-31 22:26:59.316498	2014-03-31 22:26:59.394072	27	199	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
231	8e7ba4a8-b923-11e3-8cee-2d3cb1fb0bbd	2014-03-31 22:26:51.711269	2014-03-31 22:26:51.781214	27	187	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
262	b2fc7370-b923-11e3-8df6-2d3cb1fb0bbd	2014-03-31 22:27:53.836602	2014-03-31 22:27:53.906298	55	216	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
232	8ef8fa48-b923-11e3-8cf5-2d3cb1fb0bbd	2014-03-31 22:26:52.530723	2014-03-31 22:26:52.585307	27	188	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
244	93393a28-b923-11e3-8d47-2d3cb1fb0bbd	2014-03-31 22:26:59.663931	2014-03-31 22:26:59.734756	27	200	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
233	8f1f6660-b923-11e3-8cfc-2d3cb1fb0bbd	2014-03-31 22:26:52.784127	2014-03-31 22:26:52.847911	27	189	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
245	9352c4e8-b923-11e3-8d4e-2d3cb1fb0bbd	2014-03-31 22:26:59.832526	2014-03-31 22:26:59.876945	27	198	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
255	b1cbe35a-b923-11e3-8d99-2d3cb1fb0bbd	2014-03-31 22:27:51.417431	2014-03-31 22:27:51.480352	55	209	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
234	8f5f5f36-b923-11e3-8d03-2d3cb1fb0bbd	2014-03-31 22:26:53.203468	2014-03-31 22:26:53.274167	27	190	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
235	8cef0efe-b923-11e3-8cc2-2d3cb1fb0bbd	2014-03-31 22:26:53.245463	2014-03-31 22:26:53.293319	27	191	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
246	96b29136-b923-11e3-8d56-2d3cb1fb0bbd	2014-03-31 22:27:05.490379	2014-03-31 22:27:05.543854	27	201	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
236	8b234e8c-b923-11e3-8c9e-2d3cb1fb0bbd	2014-03-31 22:26:54.207923	2014-03-31 22:26:54.27979	27	192	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
268	b290853e-b923-11e3-8de6-2d3cb1fb0bbd	2014-03-31 22:27:56.199609	2014-03-31 22:27:56.265466	55	222	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
237	9029d8ec-b923-11e3-8d16-2d3cb1fb0bbd	2014-03-31 22:26:54.529084	2014-03-31 22:26:54.602606	27	193	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
247	96df151c-b923-11e3-8d5d-2d3cb1fb0bbd	2014-03-31 22:27:05.783225	2014-03-31 22:27:05.826445	27	202	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
263	b2821ff8-b923-11e3-8de0-2d3cb1fb0bbd	2014-03-31 22:27:54.700836	2014-03-31 22:27:54.751511	55	217	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
256	b1d0bc18-b923-11e3-8d9b-2d3cb1fb0bbd	2014-03-31 22:27:51.491181	2014-03-31 22:27:51.571101	55	210	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
248	96e7fce0-b923-11e3-8d63-2d3cb1fb0bbd	2014-03-31 22:27:05.853393	2014-03-31 22:27:05.933333	27	203	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
249	96f131a2-b923-11e3-8d6a-2d3cb1fb0bbd	2014-03-31 22:27:05.901415	2014-03-31 22:27:05.947929	27	204	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
257	b1d58068-b923-11e3-8d9d-2d3cb1fb0bbd	2014-03-31 22:27:51.540795	2014-03-31 22:27:51.588739	55	211	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
250	96f9d26c-b923-11e3-8d71-2d3cb1fb0bbd	2014-03-31 22:27:05.957231	2014-03-31 22:27:06.009429	27	205	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
264	b3cf05a6-b923-11e3-8e22-2d3cb1fb0bbd	2014-03-31 22:27:54.758862	2014-03-31 22:27:54.811936	55	218	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
258	b1da4f30-b923-11e3-8d9f-2d3cb1fb0bbd	2014-03-31 22:27:51.655559	2014-03-31 22:27:51.731257	55	212	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
269	b3de633e-b923-11e3-8e26-2d3cb1fb0bbd	2014-03-31 22:27:56.420996	2014-03-31 22:27:56.487933	55	223	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
259	b253f790-b923-11e3-8dd2-2d3cb1fb0bbd	2014-03-31 22:27:52.412086	2014-03-31 22:27:52.478002	55	213	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
265	b2f7a958-b923-11e3-8df4-2d3cb1fb0bbd	2014-03-31 22:27:55.290101	2014-03-31 22:27:55.355841	55	219	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
273	b56e1776-b923-11e3-8e68-2d3cb1fb0bbd	2014-03-31 22:27:59.018844	2014-03-31 22:27:59.062708	55	227	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
270	b3f14904-b923-11e3-8e2c-2d3cb1fb0bbd	2014-03-31 22:27:56.525929	2014-03-31 22:27:56.588503	55	224	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
266	b26a27fe-b923-11e3-8dd6-2d3cb1fb0bbd	2014-03-31 22:27:55.888359	2014-03-31 22:27:55.96237	55	220	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
276	b58abf16-b923-11e3-8e74-2d3cb1fb0bbd	2014-03-31 22:28:00.516179	2014-03-31 22:28:00.575204	55	230	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
274	b62b10c4-b923-11e3-8e8a-2d3cb1fb0bbd	2014-03-31 22:27:59.455893	2014-03-31 22:27:59.526711	55	228	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
271	b314824e-b923-11e3-8e00-2d3cb1fb0bbd	2014-03-31 22:27:57.508225	2014-03-31 22:27:57.576733	55	225	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
281	b59edbcc-b923-11e3-8e7a-2d3cb1fb0bbd	2014-03-31 22:28:01.616104	2014-03-31 22:28:01.686372	55	235	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
280	b6cd7e5e-b923-11e3-8ea6-2d3cb1fb0bbd	2014-03-31 22:28:01.553031	2014-03-31 22:28:01.606413	55	234	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
277	b3014468-b923-11e3-8df8-2d3cb1fb0bbd	2014-03-31 22:28:00.878865	2014-03-31 22:28:00.939498	55	231	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
275	b286e6a0-b923-11e3-8de2-2d3cb1fb0bbd	2014-03-31 22:28:00.424942	2014-03-31 22:28:00.49507	55	229	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
278	b577891e-b923-11e3-8e6c-2d3cb1fb0bbd	2014-03-31 22:28:01.416476	2014-03-31 22:28:01.524714	55	232	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
279	b6ba4ffa-b923-11e3-8e9e-2d3cb1fb0bbd	2014-03-31 22:28:01.480357	2014-03-31 22:28:01.543713	55	233	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
282	b76320a8-b923-11e3-8ec7-2d3cb1fb0bbd	2014-03-31 22:28:02.587898	2014-03-31 22:28:02.653995	55	236	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
283	b88442fa-b923-11e3-8f05-2d3cb1fb0bbd	2014-03-31 22:28:03.597501	2014-03-31 22:28:03.663827	55	237	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
284	b913dd7a-b923-11e3-8f27-2d3cb1fb0bbd	2014-03-31 22:28:04.580576	2014-03-31 22:28:04.6629	55	238	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
286	b8a5df32-b923-11e3-8f13-2d3cb1fb0bbd	2014-03-31 22:28:04.67447	2014-03-31 22:28:04.757552	55	240	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
285	b75e4b50-b923-11e3-8ec5-2d3cb1fb0bbd	2014-03-31 22:28:04.62317	2014-03-31 22:28:04.711671	55	239	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
288	b9dcf7d2-b923-11e3-8f5f-2d3cb1fb0bbd	2014-03-31 22:28:06.821623	2014-03-31 22:28:06.884594	55	242	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
287	b9c9e26e-b923-11e3-8f57-2d3cb1fb0bbd	2014-03-31 22:28:06.776924	2014-03-31 22:28:06.853669	55	241	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
289	bb4bea4c-b923-11e3-8fc2-2d3cb1fb0bbd	2014-03-31 22:28:06.905255	2014-03-31 22:28:06.945911	55	220	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
290	bb0468b6-b923-11e3-8fa3-2d3cb1fb0bbd	2014-03-31 22:28:07.661194	2014-03-31 22:28:07.733906	55	243	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
310	c0a7cbc8-b923-11e3-90f9-2d3cb1fb0bbd	2014-03-31 22:28:15.891449	2014-03-31 22:28:16.019541	55	260	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
311	c0b04d98-b923-11e3-90ff-2d3cb1fb0bbd	2014-03-31 22:28:15.983929	2014-03-31 22:28:16.052972	55	221	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
291	b7f7dd7e-b923-11e3-8edf-2d3cb1fb0bbd	2014-03-31 22:28:08.888411	2014-03-31 22:28:09.238459	55	244	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
293	bb2f950e-b923-11e3-8fb5-2d3cb1fb0bbd	2014-03-31 22:28:09.152543	2014-03-31 22:28:09.302395	55	246	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
294	baff94a8-b923-11e3-8fa1-2d3cb1fb0bbd	2014-03-31 22:28:09.19836	2014-03-31 22:28:09.346336	55	247	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
292	baec5fb4-b923-11e3-8f99-2d3cb1fb0bbd	2014-03-31 22:28:09.014105	2014-03-31 22:28:09.356276	55	245	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
312	c0e4e684-b923-11e3-9107-2d3cb1fb0bbd	2014-03-31 22:28:16.29693	2014-03-31 22:28:16.458191	55	261	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
313	bec545ec-b923-11e3-908d-2d3cb1fb0bbd	2014-03-31 22:28:17.066619	2014-03-31 22:28:17.146302	55	262	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
296	b7ee290a-b923-11e3-8edb-2d3cb1fb0bbd	2014-03-31 22:28:09.538789	2014-03-31 22:28:10.272046	55	249	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
295	b9b6945c-b923-11e3-8f4f-2d3cb1fb0bbd	2014-03-31 22:28:09.363012	2014-03-31 22:28:10.326314	55	248	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
297	b8015188-b923-11e3-8ee3-2d3cb1fb0bbd	2014-03-31 22:28:09.669529	2014-03-31 22:28:10.334232	55	250	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
298	bba9f1a0-b923-11e3-8fdc-2d3cb1fb0bbd	2014-03-31 22:28:10.21731	2014-03-31 22:28:10.540131	55	251	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
299	b8977762-b923-11e3-8f0d-2d3cb1fb0bbd	2014-03-31 22:28:10.507589	2014-03-31 22:28:10.588145	55	236	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
314	c1ae95e2-b923-11e3-9128-2d3cb1fb0bbd	2014-03-31 22:28:17.707343	2014-03-31 22:28:17.79778	55	263	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
315	c1b7281a-b923-11e3-912e-2d3cb1fb0bbd	2014-03-31 22:28:17.753295	2014-03-31 22:28:17.853846	55	264	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
300	bb0929a0-b923-11e3-8fa5-2d3cb1fb0bbd	2014-03-31 22:28:10.556178	2014-03-31 22:28:11.286679	55	252	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
301	b8890470-b923-11e3-8f07-2d3cb1fb0bbd	2014-03-31 22:28:10.638425	2014-03-31 22:28:11.294217	55	253	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
302	bba0558c-b923-11e3-8fd8-2d3cb1fb0bbd	2014-03-31 22:28:11.724156	2014-03-31 22:28:11.76755	55	214	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
303	bbb39872-b923-11e3-8fe0-2d3cb1fb0bbd	2014-03-31 22:28:11.868626	2014-03-31 22:28:11.909044	55	232	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
316	c1fdf592-b923-11e3-9136-2d3cb1fb0bbd	2014-03-31 22:28:18.127856	2014-03-31 22:28:18.214611	55	265	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
304	be711bf2-b923-11e3-906e-2d3cb1fb0bbd	2014-03-31 22:28:12.568787	2014-03-31 22:28:12.657561	55	254	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
305	bdf98eb6-b923-11e3-904e-2d3cb1fb0bbd	2014-03-31 22:28:12.775374	2014-03-31 22:28:12.839798	55	255	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
317	bfdd0302-b923-11e3-90cc-2d3cb1fb0bbd	2014-03-31 22:28:18.848381	2014-03-31 22:28:18.920143	55	266	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
306	be9edb46-b923-11e3-907e-2d3cb1fb0bbd	2014-03-31 22:28:13.724728	2014-03-31 22:28:13.850425	55	256	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
307	bf9551d8-b923-11e3-90b3-2d3cb1fb0bbd	2014-03-31 22:28:14.090803	2014-03-31 22:28:14.173737	55	257	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
308	baf13020-b923-11e3-8f9b-2d3cb1fb0bbd	2014-03-31 22:28:14.626664	2014-03-31 22:28:14.701067	55	258	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
309	bea87ac0-b923-11e3-9080-2d3cb1fb0bbd	2014-03-31 22:28:14.665384	2014-03-31 22:28:14.720192	55	259	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
318	c077ad08-b923-11e3-90e4-2d3cb1fb0bbd	2014-03-31 22:28:19.866326	2014-03-31 22:28:19.969308	55	267	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
319	c08af0ac-b923-11e3-90ec-2d3cb1fb0bbd	2014-03-31 22:28:19.917449	2014-03-31 22:28:20.009369	55	268	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
320	c35db792-b923-11e3-9181-2d3cb1fb0bbd	2014-03-31 22:28:20.447728	2014-03-31 22:28:20.513339	55	269	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
322	c2f9f6f8-b923-11e3-9171-2d3cb1fb0bbd	2014-03-31 22:28:21.386584	\N	55	254	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
323	c3c459f2-b923-11e3-91a0-2d3cb1fb0bbd	2014-03-31 22:28:23.874879	\N	55	271	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
324	c2e6a49a-b923-11e3-9169-2d3cb1fb0bbd	2014-03-31 22:28:24.558861	\N	55	272	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
321	c2d37406-b923-11e3-9161-2d3cb1fb0bbd	2014-03-31 22:28:21.027644	2014-03-31 22:28:24.600335	55	270	\N	\N	\N	2014-04-28 02:25:11.208693+00	2014-04-28 02:25:11.245418+00
\.


--
-- Name: telephony_call_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('telephony_call_id_seq', 330, true);


--
-- Data for Name: telephony_gateway; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY telephony_gateway (id, number_top, number_bottom, sofia_string, extra_string, name, created_at, updated_at, is_goip, gateway_prefix) FROM stdin;
2	0	0	sofia/gateway/goip	bridge_early_media=true,hangup_after_bridge=true	goip	2014-04-29 18:37:47.682254+00	2014-04-29 18:37:47.68227+00	\N	\N
1	0	0	sofia/gateway/switch2voip/	bridge_early_media=true,hangup_after_bridge=true	switch2voip	2014-04-28 02:27:29.478176+00	2014-04-30 06:26:05.332304+00	\N	\N
\.


--
-- Name: telephony_gateway_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('telephony_gateway_id_seq', 2, true);


--
-- Data for Name: telephony_message; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY telephony_message (id, message_uuid, sendtime, text, from_phonenumber_id, to_phonenumber_id, onairprogram_id, created_at, updated_at) FROM stdin;
1	242987492874923874	2014-04-27 18:55:23	slkfksjhfksjhf	2	4	\N	2014-04-28 02:25:11.269711+00	2014-04-28 02:25:11.270327+00
\.


--
-- Name: telephony_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('telephony_message_id_seq', 1, true);


--
-- Data for Name: telephony_phonenumber; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY telephony_phonenumber (id, carrier, countrycode, number, raw_number, number_type, created_at, updated_at) FROM stdin;
274	tmobile	1	6176424223	6176424223	0	2014-04-29 18:22:04.175494+00	2014-04-29 18:22:04.175505+00
275	\N	\N	3124680992	3124680992	\N	2014-04-30 06:32:20.279293+00	2014-04-30 06:32:20.2793+00
276	tmobile	1	3102544951	3102544951	0	2014-05-01 01:00:10.32739+00	2014-05-01 01:00:10.327411+00
277	credo	1	6039698711	6039698711	0	2014-05-01 01:00:56.896843+00	2014-05-01 01:00:56.896853+00
1	utl	256	417744800	0417744800	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
2	utl	256	417744801	0417744801	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
3	utl	256	417744802	0417744802	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
4	utl	256	417744803	0417744803	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
5	utl	256	417744804	0417744804	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
18	MTN	256	785128690	0785128690	0	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
110	\N	\N	911713344202910	911713344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
21	\N	\N	0417744819	0417744819	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
22	\N	\N	9510785128690	9510785128690	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
23	\N	\N	0417744818	0417744818	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
24	\N	\N	0417744817	0417744817	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
25	MTN	256	785128654	0785128654	0	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
26	\N	\N	9510785128654	9510785128654	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
27	\N	\N	1000	1000	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
28	\N	\N	00448451547428	00448451547428	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
29	\N	\N	000441415308238	000441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
30	\N	\N	0900441415308238	0900441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
31	\N	\N	900441415308238	900441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
32	\N	\N	9900441415308238	9900441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
33	\N	\N	99900441415308238	99900441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
34	\N	\N	999900441415308238	999900441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
35	\N	\N	9999000441415308238	9999000441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
36	\N	\N	00441415308238	00441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
37	\N	\N	441415308238	441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
38	\N	\N	944441415308238	944441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
39	\N	\N	91441415308238	91441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
40	\N	\N	44441415308238	44441415308238	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
41	\N	\N	12537850502	12537850502	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
42	\N	\N	00012537850502	00012537850502	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
43	\N	\N	90012537850502	90012537850502	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
44	\N	\N	090012537850502	090012537850502	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
45	\N	\N	990012537850502	990012537850502	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
46	\N	\N	9990012537850502	9990012537850502	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
47	\N	\N	99990012537850502	99990012537850502	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
48	\N	\N	999900012537850502	999900012537850502	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
49	\N	\N	94412537850502	94412537850502	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
50	\N	\N	00972597828253	00972597828253	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
51	\N	\N	000972597828253	000972597828253	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
52	\N	\N	900972597828253	900972597828253	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
53	\N	\N	011972597828253	011972597828253	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
54	\N	\N	810972597828253	810972597828253	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
55	\N	\N	1001	1001	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
56	\N	\N	972544757644	972544757644	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
57	\N	\N	00972544757644	00972544757644	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
58	\N	\N	0-0972544757644	0-0972544757644	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
59	\N	\N	000972544757644	000972544757644	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
60	\N	\N	900972544757644	900972544757644	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
61	\N	\N	00441904890604	00441904890604	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
62	\N	\N	00033170727895	00033170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
63	\N	\N	00933170727895	00933170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
64	\N	\N	001133170727895	001133170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
65	\N	\N	00833170727895	00833170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
66	\N	\N	00333170727895	00333170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
67	\N	\N	000033170727895	000033170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
68	\N	\N	90033170727895	90033170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
69	\N	\N	80033170727895	80033170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
70	\N	\N	70033170727895	70033170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
71	\N	\N	60033170727895	60033170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
72	\N	\N	50033170727895	50033170727895	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
73	\N	\N	00972599688424	00972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
74	\N	\N	000441904890604	000441904890604	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
75	\N	\N	00551668834019	00551668834019	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
76	\N	\N	00375239886001	00375239886001	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
77	\N	\N	00443339660049	00443339660049	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
78	\N	\N	00479852157987	00479852157987	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
79	\N	\N	00496969066369	00496969066369	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
80	\N	\N	00913344202910	00913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
81	\N	\N	99913344202910	99913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
82	\N	\N	50013344202910	50013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
83	\N	\N	70013344202910	70013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
84	\N	\N	01413344202910	01413344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
85	\N	\N	10113344202910	10113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
86	\N	\N	10013344202910	10013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
87	\N	\N	01913344202910	01913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
88	\N	\N	01813344202910	01813344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
89	\N	\N	800813344202910	800813344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
90	\N	\N	99713344202910	99713344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
91	\N	\N	81013344202910	81013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
92	\N	\N	800413344202910	800413344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
93	\N	\N	88813344202910	88813344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
94	\N	\N	99413344202910	99413344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
95	\N	\N	99013344202910	99013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
96	\N	\N	800713344202910	800713344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
97	\N	\N	800513344202910	800513344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
98	\N	\N	800913344202910	800913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
99	\N	\N	200813344202910	200813344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
100	\N	\N	20013344202910	20013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
101	\N	\N	900213344202910	900213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
102	\N	\N	100113344202910	100113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
103	\N	\N	60313344202910	60313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
104	\N	\N	10813344202910	10813344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
105	\N	\N	90013344202910	90013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
106	\N	\N	400513344202910	400513344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
107	\N	\N	01213344202910	01213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
108	\N	\N	971013344202910	971013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
109	\N	\N	400313344202910	400313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
111	\N	\N	60013344202910	60013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
112	\N	\N	800313344202910	800313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
113	\N	\N	21113344202910	21113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
114	\N	\N	01013344202910	01013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
115	\N	\N	501113344202910	501113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
116	\N	\N	801713344202910	801713344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
117	\N	\N	981013344202910	981013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
118	\N	\N	70913344202910	70913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
119	\N	\N	700313344202910	700313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
120	\N	\N	681113344202910	681113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
121	\N	\N	500613344202910	500613344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
122	\N	\N	60613344202910	60613344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
123	\N	\N	500513344202910	500513344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
124	\N	\N	900713344202910	900713344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
125	\N	\N	60713344202910	60713344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
126	\N	\N	600713344202910	600713344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
127	\N	\N	801513344202910	801513344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
128	\N	\N	40713344202910	40713344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
129	\N	\N	900613344202910	900613344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
130	\N	\N	900913344202910	900913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
131	\N	\N	30613344202910	30613344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
132	\N	\N	971113344202910	971113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
133	\N	\N	700113344202910	700113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
134	\N	\N	700513344202910	700513344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
135	\N	\N	100413344202910	100413344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
136	\N	\N	601113344202910	601113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
137	\N	\N	981113344202910	981113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
138	\N	\N	601813344202910	601813344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
139	\N	\N	181013344202910	181013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
140	\N	\N	801113344202910	801113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
141	\N	\N	01513344202910	01513344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
142	\N	\N	200913344202910	200913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
143	\N	\N	700813344202910	700813344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
144	\N	\N	581013344202910	581013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
145	\N	\N	10413344202910	10413344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
146	\N	\N	500213344202910	500213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
147	\N	\N	10213344202910	10213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
148	\N	\N	901813344202910	901813344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
149	\N	\N	991113344202910	991113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
150	\N	\N	70813344202910	70813344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
151	\N	\N	700913344202910	700913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
152	\N	\N	681013344202910	681013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
153	\N	\N	80613344202910	80613344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
154	\N	\N	800213344202910	800213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
155	\N	\N	701413344202910	701413344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
156	\N	\N	801613344202910	801613344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
157	\N	\N	50913344202910	50913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
158	\N	\N	41113344202910	41113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
159	\N	\N	80113344202910	80113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
160	\N	\N	80913344202910	80913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
161	\N	\N	101013344202910	101013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
162	\N	\N	20213344202910	20213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
163	\N	\N	601313344202910	601313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
164	\N	\N	441013344202910	441013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
165	\N	\N	200513344202910	200513344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
166	\N	\N	500813344202910	500813344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
167	\N	\N	100613344202910	100613344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
168	\N	\N	200013344202910	200013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
169	\N	\N	30113344202910	30113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
170	\N	\N	49013344202910	49013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
171	\N	\N	300513344202910	300513344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
172	\N	\N	411313344202910	411313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
173	\N	\N	200413344202910	200413344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
174	\N	\N	601213344202910	601213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
175	\N	\N	701113344202910	701113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
176	\N	\N	601413344202910	601413344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
177	\N	\N	500113344202910	500113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
178	\N	\N	79913344202910	79913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
179	\N	\N	51113344202910	51113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
180	\N	\N	511313344202910	511313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
181	\N	\N	40213344202910	40213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
182	\N	\N	30413344202910	30413344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
183	\N	\N	300313344202910	300313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
184	\N	\N	701313344202910	701313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
185	\N	\N	700713344202910	700713344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
186	\N	\N	200613344202910	200613344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
187	\N	\N	2340013344202910	2340013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
188	\N	\N	40113344202910	40113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
189	\N	\N	691113344202910	691113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
190	\N	\N	901313344202910	901313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
191	\N	\N	29013344202910	29013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
192	\N	\N	401313344202910	401313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
193	\N	\N	20913344202910	20913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
194	\N	\N	711113344202910	711113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
195	\N	\N	100513344202910	100513344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
196	\N	\N	551013344202910	551013344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
197	\N	\N	901113344202910	901113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
198	\N	\N	100913344202910	100913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
199	\N	\N	301113344202910	301113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
200	\N	\N	611313344202910	611313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
201	\N	\N	901213344202910	901213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
202	\N	\N	80213344202910	80213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
203	\N	\N	80313344202910	80313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
204	\N	\N	80513344202910	80513344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
205	\N	\N	800113344202910	800113344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
206	\N	\N	89913344202910	89913344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
207	\N	\N	200213344202910	200213344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
208	\N	\N	711313344202910	711313344202910	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
209	\N	\N	009972599688424	009972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
210	\N	\N	099972599688424	099972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
211	\N	\N	16972599688424	16972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
212	\N	\N	000972599688424	000972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
213	\N	\N	03972599688424	03972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
214	\N	\N	888972599688424	888972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
215	\N	\N	001972599688424	001972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
216	\N	\N	012972599688424	012972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
217	\N	\N	997972599688424	997972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
218	\N	\N	500972599688424	500972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
219	\N	\N	9014972599688424	9014972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
220	\N	\N	09972599688424	09972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
221	\N	\N	700972599688424	700972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
222	\N	\N	611972599688424	611972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
223	\N	\N	300972599688424	300972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
224	\N	\N	23400972599688424	23400972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
225	\N	\N	019972599688424	019972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
226	\N	\N	9007972599688424	9007972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
227	\N	\N	7011972599688424	7011972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
228	\N	\N	9010972599688424	9010972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
229	\N	\N	994972599688424	994972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
230	\N	\N	101972599688424	101972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
231	\N	\N	013972599688424	013972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
232	\N	\N	6011972599688424	6011972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
233	\N	\N	9710972599688424	9710972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
234	\N	\N	9013972599688424	9013972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
235	\N	\N	9003972599688424	9003972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
236	\N	\N	8008972599688424	8008972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
237	\N	\N	8004972599688424	8004972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
238	\N	\N	705972599688424	705972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
239	\N	\N	8007972599688424	8007972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
240	\N	\N	508972599688424	508972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
241	\N	\N	406972599688424	406972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
242	\N	\N	4001972599688424	4001972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
243	\N	\N	119972599688424	119972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
244	\N	\N	701972599688424	701972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
245	\N	\N	8011972599688424	8011972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
246	\N	\N	7810972599688424	7810972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
247	\N	\N	008972599688424	008972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
248	\N	\N	8018972599688424	8018972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
249	\N	\N	9008972599688424	9008972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
250	\N	\N	602972599688424	602972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
251	\N	\N	6610972599688424	6610972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
252	\N	\N	118972599688424	118972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
253	\N	\N	8005972599688424	8005972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
254	\N	\N	9012972599688424	9012972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
255	\N	\N	7000972599688424	7000972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
256	\N	\N	8811972599688424	8811972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
257	\N	\N	8003972599688424	8003972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
258	\N	\N	810972599688424	810972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
259	\N	\N	8711972599688424	8711972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
260	\N	\N	706972599688424	706972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
261	\N	\N	8019972599688424	8019972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
262	\N	\N	4118972599688424	4118972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
263	\N	\N	9006972599688424	9006972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
264	\N	\N	3009972599688424	3009972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
265	\N	\N	9011972599688424	9011972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
266	\N	\N	1117972599688424	1117972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
267	\N	\N	7007972599688424	7007972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
268	\N	\N	490972599688424	490972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
269	\N	\N	303972599688424	303972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
270	\N	\N	3000972599688424	3000972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
271	\N	\N	902972599688424	902972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
272	\N	\N	9811972599688424	9811972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
273	\N	\N	309972599688424	309972599688424	\N	2014-04-28 02:25:11.271065+00	2014-04-28 02:25:11.28631+00
\.


--
-- Name: telephony_phonenumber_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('telephony_phonenumber_id_seq', 277, true);


--
-- Data for Name: user_details; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_details (id, age, phone, url, location, bio, gender_code, created_time) FROM stdin;
1	25	\N	http://example.com	Kampala		1	2014-03-13 00:58:24.852121
2	\N	\N	\N	\N	\N	\N	2014-03-24 13:17:17.14004
3	\N	\N	\N	\N	\N	\N	2014-03-24 22:15:44.749781
\.


--
-- Name: user_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_details_id_seq', 3, true);


--
-- Data for Name: user_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_user (id, name, email, openid, activation_key, created_time, last_accessed, avatar, password, role_code, status_code, user_detail_id) FROM stdin;
3	csik	csik@media.mit.edu	\N	\N	2014-03-13 10:50:26.234436	\N	\N	pbkdf2:sha1:1000$nBYeKejf$a5f7fb4330f74d4d04d0804a367caafd13869fec	0	0	\N
4	jude	jude.mukundane@gmail.com	\N	\N	2014-03-13 11:01:28.014768	\N	\N	pbkdf2:sha1:1000$wvbzcWuq$41d949423869fb344f47e22cb2571cca5ff5bdea	0	0	\N
6	jude123	jude19love@gmail.com	\N	\N	2014-03-24 00:00:00	\N	\N	pbkdf2:sha1:1000$FkhDfuaI$1ac3e7000eae7ee2f4fb41ab4534ff958adf7594	0	0	2
1	admin	admin@example.com	\N	\N	2014-03-13 00:58:24.853678	\N	\N	pbkdf2:sha1:1000$hQTYeJZ2$42ba7d6445e417076df450fc3f373e6b702b24e3	0	2	1
7	jlev	josh@levinger.net	\N	\N	2014-03-24 00:00:00	\N	\N	pbkdf2:sha1:1000$UViL9VKx$7cdd2879302220a1e9299cbd9dc781ec7cc22a42	0	2	3
\.


--
-- Name: user_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_user_id_seq', 7, true);


--
-- Name: onair_program_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY onair_program
    ADD CONSTRAINT onair_program_pkey PRIMARY KEY (id);


--
-- Name: radio_episode_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_episode
    ADD CONSTRAINT radio_episode_pkey PRIMARY KEY (id);


--
-- Name: radio_language_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_language
    ADD CONSTRAINT radio_language_pkey PRIMARY KEY (id);


--
-- Name: radio_location_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_location
    ADD CONSTRAINT radio_location_pkey PRIMARY KEY (id);


--
-- Name: radio_network_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_network
    ADD CONSTRAINT radio_network_pkey PRIMARY KEY (id);


--
-- Name: radio_paddingcontent_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_paddingcontent
    ADD CONSTRAINT radio_paddingcontent_pkey PRIMARY KEY (id);


--
-- Name: radio_person_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_person
    ADD CONSTRAINT radio_person_pkey PRIMARY KEY (id);


--
-- Name: radio_program_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_program
    ADD CONSTRAINT radio_program_pkey PRIMARY KEY (id);


--
-- Name: radio_programtype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_programtype
    ADD CONSTRAINT radio_programtype_pkey PRIMARY KEY (id);


--
-- Name: radio_recording_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_recording
    ADD CONSTRAINT radio_recording_pkey PRIMARY KEY (id);


--
-- Name: radio_role_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_role
    ADD CONSTRAINT radio_role_pkey PRIMARY KEY (id);


--
-- Name: radio_scheduledblock_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_scheduledblock
    ADD CONSTRAINT radio_scheduledblock_pkey PRIMARY KEY (id);


--
-- Name: radio_scheduledprogram_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_scheduledprogram
    ADD CONSTRAINT radio_scheduledprogram_pkey PRIMARY KEY (id);


--
-- Name: radio_station_api_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_station
    ADD CONSTRAINT radio_station_api_key_key UNIQUE (api_key);


--
-- Name: radio_station_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_station
    ADD CONSTRAINT radio_station_pkey PRIMARY KEY (id);


--
-- Name: radio_stationanalytic_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY radio_stationanalytic
    ADD CONSTRAINT radio_stationanalytic_pkey PRIMARY KEY (id);


--
-- Name: telephony_call_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY telephony_call
    ADD CONSTRAINT telephony_call_pkey PRIMARY KEY (id);


--
-- Name: telephony_gateway_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY telephony_gateway
    ADD CONSTRAINT telephony_gateway_pkey PRIMARY KEY (id);


--
-- Name: telephony_message_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY telephony_message
    ADD CONSTRAINT telephony_message_pkey PRIMARY KEY (id);


--
-- Name: telephony_phonenumber_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY telephony_phonenumber
    ADD CONSTRAINT telephony_phonenumber_pkey PRIMARY KEY (id);


--
-- Name: user_details_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_details
    ADD CONSTRAINT user_details_pkey PRIMARY KEY (id);


--
-- Name: user_user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_user
    ADD CONSTRAINT user_user_email_key UNIQUE (email);


--
-- Name: user_user_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_user
    ADD CONSTRAINT user_user_name_key UNIQUE (name);


--
-- Name: user_user_openid_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_user
    ADD CONSTRAINT user_user_openid_key UNIQUE (openid);


--
-- Name: user_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_user
    ADD CONSTRAINT user_user_pkey PRIMARY KEY (id);


--
-- Name: onair_program_episode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY onair_program
    ADD CONSTRAINT onair_program_episode_id_fkey FOREIGN KEY (episode_id) REFERENCES radio_episode(id);


--
-- Name: onair_program_scheduledprogram_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY onair_program
    ADD CONSTRAINT onair_program_scheduledprogram_id_fkey FOREIGN KEY (scheduledprogram_id) REFERENCES radio_scheduledprogram(id);


--
-- Name: radio_episode_program_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_episode
    ADD CONSTRAINT radio_episode_program_id_fkey FOREIGN KEY (program_id) REFERENCES radio_program(id);


--
-- Name: radio_episode_recording_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_episode
    ADD CONSTRAINT radio_episode_recording_id_fkey FOREIGN KEY (recording_id) REFERENCES radio_recording(id);


--
-- Name: radio_incominggateway_incominggateway_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_incominggateway
    ADD CONSTRAINT radio_incominggateway_incominggateway_id_fkey FOREIGN KEY (incominggateway_id) REFERENCES telephony_gateway(id);


--
-- Name: radio_incominggateway_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_incominggateway
    ADD CONSTRAINT radio_incominggateway_station_id_fkey FOREIGN KEY (station_id) REFERENCES radio_station(id);


--
-- Name: radio_networkadmins_network_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_networkadmins
    ADD CONSTRAINT radio_networkadmins_network_id_fkey FOREIGN KEY (network_id) REFERENCES radio_network(id);


--
-- Name: radio_networkadmins_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_networkadmins
    ADD CONSTRAINT radio_networkadmins_user_id_fkey FOREIGN KEY (user_id) REFERENCES user_user(id);


--
-- Name: radio_networkpadding_network_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_networkpadding
    ADD CONSTRAINT radio_networkpadding_network_id_fkey FOREIGN KEY (network_id) REFERENCES radio_network(id);


--
-- Name: radio_networkpadding_paddingcontent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_networkpadding
    ADD CONSTRAINT radio_networkpadding_paddingcontent_id_fkey FOREIGN KEY (paddingcontent_id) REFERENCES radio_paddingcontent(id);


--
-- Name: radio_outgoinggateway_outgoinggateway_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_outgoinggateway
    ADD CONSTRAINT radio_outgoinggateway_outgoinggateway_id_fkey FOREIGN KEY (outgoinggateway_id) REFERENCES telephony_gateway(id);


--
-- Name: radio_outgoinggateway_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_outgoinggateway
    ADD CONSTRAINT radio_outgoinggateway_station_id_fkey FOREIGN KEY (station_id) REFERENCES radio_station(id);


--
-- Name: radio_paddingcontent_block_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_paddingcontent
    ADD CONSTRAINT radio_paddingcontent_block_id_fkey FOREIGN KEY (block_id) REFERENCES radio_scheduledblock(id);


--
-- Name: radio_paddingcontent_recording_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_paddingcontent
    ADD CONSTRAINT radio_paddingcontent_recording_id_fkey FOREIGN KEY (recording_id) REFERENCES radio_recording(id);


--
-- Name: radio_person_phone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_person
    ADD CONSTRAINT radio_person_phone_id_fkey FOREIGN KEY (phone_id) REFERENCES telephony_phonenumber(id);


--
-- Name: radio_personlanguage_language_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_personlanguage
    ADD CONSTRAINT radio_personlanguage_language_id_fkey FOREIGN KEY (language_id) REFERENCES radio_language(id);


--
-- Name: radio_personlanguage_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_personlanguage
    ADD CONSTRAINT radio_personlanguage_person_id_fkey FOREIGN KEY (person_id) REFERENCES radio_person(id);


--
-- Name: radio_program_language_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_program
    ADD CONSTRAINT radio_program_language_id_fkey FOREIGN KEY (language_id) REFERENCES radio_language(id);


--
-- Name: radio_program_program_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_program
    ADD CONSTRAINT radio_program_program_type_id_fkey FOREIGN KEY (program_type_id) REFERENCES radio_programtype(id);


--
-- Name: radio_role_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_role
    ADD CONSTRAINT radio_role_person_id_fkey FOREIGN KEY (person_id) REFERENCES radio_person(id);


--
-- Name: radio_role_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_role
    ADD CONSTRAINT radio_role_station_id_fkey FOREIGN KEY (station_id) REFERENCES radio_station(id);


--
-- Name: radio_scheduledblock_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_scheduledblock
    ADD CONSTRAINT radio_scheduledblock_station_id_fkey FOREIGN KEY (station_id) REFERENCES radio_station(id);


--
-- Name: radio_scheduledprogram_program_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_scheduledprogram
    ADD CONSTRAINT radio_scheduledprogram_program_id_fkey FOREIGN KEY (program_id) REFERENCES radio_program(id);


--
-- Name: radio_scheduledprogram_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_scheduledprogram
    ADD CONSTRAINT radio_scheduledprogram_station_id_fkey FOREIGN KEY (station_id) REFERENCES radio_station(id);


--
-- Name: radio_station_cloud_phone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_station
    ADD CONSTRAINT radio_station_cloud_phone_id_fkey FOREIGN KEY (cloud_phone_id) REFERENCES telephony_phonenumber(id);


--
-- Name: radio_station_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_station
    ADD CONSTRAINT radio_station_location_id_fkey FOREIGN KEY (location_id) REFERENCES radio_location(id);


--
-- Name: radio_station_network_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_station
    ADD CONSTRAINT radio_station_network_id_fkey FOREIGN KEY (network_id) REFERENCES radio_network(id);


--
-- Name: radio_station_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_station
    ADD CONSTRAINT radio_station_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES user_user(id);


--
-- Name: radio_station_transmitter_phone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_station
    ADD CONSTRAINT radio_station_transmitter_phone_id_fkey FOREIGN KEY (transmitter_phone_id) REFERENCES telephony_phonenumber(id);


--
-- Name: radio_stationanalytic_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_stationanalytic
    ADD CONSTRAINT radio_stationanalytic_station_id_fkey FOREIGN KEY (station_id) REFERENCES radio_station(id);


--
-- Name: radio_stationlanguage_language_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_stationlanguage
    ADD CONSTRAINT radio_stationlanguage_language_id_fkey FOREIGN KEY (language_id) REFERENCES radio_language(id);


--
-- Name: radio_stationlanguage_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY radio_stationlanguage
    ADD CONSTRAINT radio_stationlanguage_station_id_fkey FOREIGN KEY (station_id) REFERENCES radio_station(id);


--
-- Name: telephony_call_from_phonenumber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY telephony_call
    ADD CONSTRAINT telephony_call_from_phonenumber_id_fkey FOREIGN KEY (from_phonenumber_id) REFERENCES telephony_phonenumber(id);


--
-- Name: telephony_call_onairprogram_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY telephony_call
    ADD CONSTRAINT telephony_call_onairprogram_id_fkey FOREIGN KEY (onairprogram_id) REFERENCES onair_program(id);


--
-- Name: telephony_call_to_phonenumber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY telephony_call
    ADD CONSTRAINT telephony_call_to_phonenumber_id_fkey FOREIGN KEY (to_phonenumber_id) REFERENCES telephony_phonenumber(id);


--
-- Name: telephony_message_from_phonenumber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY telephony_message
    ADD CONSTRAINT telephony_message_from_phonenumber_id_fkey FOREIGN KEY (from_phonenumber_id) REFERENCES telephony_phonenumber(id);


--
-- Name: telephony_message_onairprogram_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY telephony_message
    ADD CONSTRAINT telephony_message_onairprogram_id_fkey FOREIGN KEY (onairprogram_id) REFERENCES onair_program(id);


--
-- Name: telephony_message_to_phonenumber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY telephony_message
    ADD CONSTRAINT telephony_message_to_phonenumber_id_fkey FOREIGN KEY (to_phonenumber_id) REFERENCES telephony_phonenumber(id);


--
-- Name: user_user_user_detail_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_user
    ADD CONSTRAINT user_user_user_detail_id_fkey FOREIGN KEY (user_detail_id) REFERENCES user_details(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

