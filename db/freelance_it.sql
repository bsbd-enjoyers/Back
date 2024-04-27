-- This script was generated by the ERD tool in pgAdmin 4.
-- Please log an issue at https://redmine.postgresql.org/projects/pgadmin4/issues/new if you find any bugs, including reproduction steps.
BEGIN;


CREATE TABLE IF NOT EXISTS public."Client"
(
    client_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    client_full_name character varying(50) COLLATE pg_catalog."default",
    client_email character varying(30) COLLATE pg_catalog."default",
    client_phone character varying(30) COLLATE pg_catalog."default",
    client_service_id bigint NOT NULL,
    CONSTRAINT "Client_pkey" PRIMARY KEY (client_id)
);

CREATE TABLE IF NOT EXISTS public."Document"
(
    document_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    order_id bigint NOT NULL,
    document_name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    document_content bytea NOT NULL,
    CONSTRAINT "Document_pkey" PRIMARY KEY (document_id)
);

CREATE TABLE IF NOT EXISTS public."Feedback"
(
    feedback_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    master_id bigint NOT NULL,
    client_id bigint NOT NULL,
    feedback_score smallint NOT NULL,
    feedback_comment text COLLATE pg_catalog."default",
    CONSTRAINT "Feedback_pkey" PRIMARY KEY (feedback_id)
);

CREATE TABLE IF NOT EXISTS public."Master"
(
    master_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    master_full_name character varying(50) COLLATE pg_catalog."default",
    master_email character varying(30) COLLATE pg_catalog."default",
    master_phone character varying(30) COLLATE pg_catalog."default",
    master_detailed_info text COLLATE pg_catalog."default",
    master_service_id bigint NOT NULL,
    CONSTRAINT "Master_pkey" PRIMARY KEY (master_id)
);

CREATE TABLE IF NOT EXISTS public."Order"
(
    order_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    client_id bigint NOT NULL,
    master_id bigint NOT NULL,
    product_id bigint NOT NULL,
    order_deadline date,
    order_totalcost bigint,
    order_status character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT "Order_pkey" PRIMARY KEY (order_id)
);

CREATE TABLE IF NOT EXISTS public."Product"
(
    product_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    product_type character varying(30) COLLATE pg_catalog."default" NOT NULL,
    product_full_name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    product_client_description text COLLATE pg_catalog."default" NOT NULL,
    product_master_specification text COLLATE pg_catalog."default",
    CONSTRAINT "Product_pkey" PRIMARY KEY (product_id)
);

CREATE TABLE IF NOT EXISTS public."Service_data"
(
    service_data_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    service_data_login character varying(50) COLLATE pg_catalog."default" NOT NULL,
    service_data_password character varying(256) COLLATE pg_catalog."default" NOT NULL,
    service_data_role character varying(30) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Service_data_pkey" PRIMARY KEY (service_data_id),
    CONSTRAINT service_data_login UNIQUE (service_data_login)
);

CREATE TABLE IF NOT EXISTS public."Skill"
(
    skill_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    master_id bigint NOT NULL,
    skill_type character varying(50) COLLATE pg_catalog."default" NOT NULL,
    skill_description text COLLATE pg_catalog."default",
    CONSTRAINT "Skill_pkey" PRIMARY KEY (skill_id)
);

ALTER TABLE IF EXISTS public."Client"
    ADD CONSTRAINT "client_service-id" FOREIGN KEY (client_service_id)
    REFERENCES public."Service_data" (service_data_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public."Document"
    ADD CONSTRAINT order_id FOREIGN KEY (order_id)
    REFERENCES public."Order" (order_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public."Feedback"
    ADD CONSTRAINT client_id FOREIGN KEY (client_id)
    REFERENCES public."Client" (client_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public."Feedback"
    ADD CONSTRAINT master_id FOREIGN KEY (master_id)
    REFERENCES public."Master" (master_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public."Master"
    ADD CONSTRAINT master_service_id FOREIGN KEY (master_service_id)
    REFERENCES public."Service_data" (service_data_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public."Order"
    ADD CONSTRAINT client_id FOREIGN KEY (client_id)
    REFERENCES public."Client" (client_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Order"
    ADD CONSTRAINT master_id FOREIGN KEY (master_id)
    REFERENCES public."Master" (master_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Order"
    ADD CONSTRAINT product_id FOREIGN KEY (product_id)
    REFERENCES public."Product" (product_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Skill"
    ADD CONSTRAINT master_id FOREIGN KEY (master_id)
    REFERENCES public."Master" (master_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

END;