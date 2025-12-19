--
-- PostgreSQL database dump
--

\restrict UB4GtSOR9R7qK77yjBTMNhCafxyHkB9ILOIOaablqJ2l3bfhC4ZLt7gEe9sAc5k

-- Dumped from database version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alunos; Type: TABLE; Schema: public; Owner: totem_usuario
--

CREATE TABLE public.alunos (
    id_aluno integer NOT NULL,
    matricula character varying(20) NOT NULL,
    nome_completo character varying(150) NOT NULL,
    ja_votou boolean DEFAULT false,
    data_cadastro timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.alunos OWNER TO totem_usuario;

--
-- Name: alunos_id_aluno_seq; Type: SEQUENCE; Schema: public; Owner: totem_usuario
--

CREATE SEQUENCE public.alunos_id_aluno_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.alunos_id_aluno_seq OWNER TO totem_usuario;

--
-- Name: alunos_id_aluno_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: totem_usuario
--

ALTER SEQUENCE public.alunos_id_aluno_seq OWNED BY public.alunos.id_aluno;


--
-- Name: atendimentos; Type: TABLE; Schema: public; Owner: totem_usuario
--

CREATE TABLE public.atendimentos (
    id_atendimento integer NOT NULL,
    id_senha integer NOT NULL,
    data_atendimento timestamp without time zone NOT NULL,
    duracao integer,
    servico character varying(50) DEFAULT NULL::character varying
);


ALTER TABLE public.atendimentos OWNER TO totem_usuario;

--
-- Name: atendimentos_id_atendimento_seq; Type: SEQUENCE; Schema: public; Owner: totem_usuario
--

CREATE SEQUENCE public.atendimentos_id_atendimento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.atendimentos_id_atendimento_seq OWNER TO totem_usuario;

--
-- Name: atendimentos_id_atendimento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: totem_usuario
--

ALTER SEQUENCE public.atendimentos_id_atendimento_seq OWNED BY public.atendimentos.id_atendimento;


--
-- Name: candidatos; Type: TABLE; Schema: public; Owner: totem_usuario
--

CREATE TABLE public.candidatos (
    id_candidato integer NOT NULL,
    nome character varying(100) NOT NULL,
    numero integer NOT NULL,
    ativo boolean DEFAULT true
);


ALTER TABLE public.candidatos OWNER TO totem_usuario;

--
-- Name: candidatos_id_candidato_seq; Type: SEQUENCE; Schema: public; Owner: totem_usuario
--

CREATE SEQUENCE public.candidatos_id_candidato_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidatos_id_candidato_seq OWNER TO totem_usuario;

--
-- Name: candidatos_id_candidato_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: totem_usuario
--

ALTER SEQUENCE public.candidatos_id_candidato_seq OWNED BY public.candidatos.id_candidato;


--
-- Name: enquetes; Type: TABLE; Schema: public; Owner: totem_usuario
--

CREATE TABLE public.enquetes (
    id integer NOT NULL,
    titulo character varying(100) NOT NULL,
    descricao text,
    opcoes text,
    ativa boolean DEFAULT true,
    data_inicio timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    data_fim timestamp without time zone,
    total_votos integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.enquetes OWNER TO totem_usuario;

--
-- Name: enquetes_id_seq; Type: SEQUENCE; Schema: public; Owner: totem_usuario
--

CREATE SEQUENCE public.enquetes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.enquetes_id_seq OWNER TO totem_usuario;

--
-- Name: enquetes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: totem_usuario
--

ALTER SEQUENCE public.enquetes_id_seq OWNED BY public.enquetes.id;


--
-- Name: senhas; Type: TABLE; Schema: public; Owner: totem_usuario
--

CREATE TABLE public.senhas (
    id_senha integer NOT NULL,
    numero character varying(10) NOT NULL,
    prioridade integer DEFAULT 0 NOT NULL,
    status character varying(20) DEFAULT 'pendente'::character varying NOT NULL,
    data_emissao timestamp without time zone NOT NULL,
    servico character varying(50) DEFAULT NULL::character varying,
    idade integer,
    prior_check boolean DEFAULT false
);


ALTER TABLE public.senhas OWNER TO totem_usuario;

--
-- Name: senhas_id_senha_seq; Type: SEQUENCE; Schema: public; Owner: totem_usuario
--

CREATE SEQUENCE public.senhas_id_senha_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.senhas_id_senha_seq OWNER TO totem_usuario;

--
-- Name: senhas_id_senha_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: totem_usuario
--

ALTER SEQUENCE public.senhas_id_senha_seq OWNED BY public.senhas.id_senha;


--
-- Name: servicos; Type: TABLE; Schema: public; Owner: totem_usuario
--

CREATE TABLE public.servicos (
    id integer NOT NULL,
    nome character varying(50) NOT NULL,
    descricao text,
    documentos text,
    faq text,
    tempo_medio integer DEFAULT 20,
    data_criacao timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.servicos OWNER TO totem_usuario;

--
-- Name: servicos_id_seq; Type: SEQUENCE; Schema: public; Owner: totem_usuario
--

CREATE SEQUENCE public.servicos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.servicos_id_seq OWNER TO totem_usuario;

--
-- Name: servicos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: totem_usuario
--

ALTER SEQUENCE public.servicos_id_seq OWNED BY public.servicos.id;


--
-- Name: votos; Type: TABLE; Schema: public; Owner: totem_usuario
--

CREATE TABLE public.votos (
    id integer NOT NULL,
    enquete_id integer,
    opcao integer,
    data_voto timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    ip_hash character varying(64),
    aluno_id integer,
    candidato_id integer
);


ALTER TABLE public.votos OWNER TO totem_usuario;

--
-- Name: votos_id_seq; Type: SEQUENCE; Schema: public; Owner: totem_usuario
--

CREATE SEQUENCE public.votos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.votos_id_seq OWNER TO totem_usuario;

--
-- Name: votos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: totem_usuario
--

ALTER SEQUENCE public.votos_id_seq OWNED BY public.votos.id;


--
-- Name: alunos id_aluno; Type: DEFAULT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.alunos ALTER COLUMN id_aluno SET DEFAULT nextval('public.alunos_id_aluno_seq'::regclass);


--
-- Name: atendimentos id_atendimento; Type: DEFAULT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.atendimentos ALTER COLUMN id_atendimento SET DEFAULT nextval('public.atendimentos_id_atendimento_seq'::regclass);


--
-- Name: candidatos id_candidato; Type: DEFAULT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.candidatos ALTER COLUMN id_candidato SET DEFAULT nextval('public.candidatos_id_candidato_seq'::regclass);


--
-- Name: enquetes id; Type: DEFAULT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.enquetes ALTER COLUMN id SET DEFAULT nextval('public.enquetes_id_seq'::regclass);


--
-- Name: senhas id_senha; Type: DEFAULT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.senhas ALTER COLUMN id_senha SET DEFAULT nextval('public.senhas_id_senha_seq'::regclass);


--
-- Name: servicos id; Type: DEFAULT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.servicos ALTER COLUMN id SET DEFAULT nextval('public.servicos_id_seq'::regclass);


--
-- Name: votos id; Type: DEFAULT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.votos ALTER COLUMN id SET DEFAULT nextval('public.votos_id_seq'::regclass);


--
-- Name: alunos alunos_matricula_key; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.alunos
    ADD CONSTRAINT alunos_matricula_key UNIQUE (matricula);


--
-- Name: alunos alunos_pkey; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.alunos
    ADD CONSTRAINT alunos_pkey PRIMARY KEY (id_aluno);


--
-- Name: atendimentos atendimentos_pkey; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.atendimentos
    ADD CONSTRAINT atendimentos_pkey PRIMARY KEY (id_atendimento);


--
-- Name: candidatos candidatos_numero_key; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.candidatos
    ADD CONSTRAINT candidatos_numero_key UNIQUE (numero);


--
-- Name: candidatos candidatos_pkey; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.candidatos
    ADD CONSTRAINT candidatos_pkey PRIMARY KEY (id_candidato);


--
-- Name: enquetes enquetes_pkey; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.enquetes
    ADD CONSTRAINT enquetes_pkey PRIMARY KEY (id);


--
-- Name: senhas senhas_numero_key; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.senhas
    ADD CONSTRAINT senhas_numero_key UNIQUE (numero);


--
-- Name: senhas senhas_pkey; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.senhas
    ADD CONSTRAINT senhas_pkey PRIMARY KEY (id_senha);


--
-- Name: servicos servicos_nome_key; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.servicos
    ADD CONSTRAINT servicos_nome_key UNIQUE (nome);


--
-- Name: servicos servicos_pkey; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.servicos
    ADD CONSTRAINT servicos_pkey PRIMARY KEY (id);


--
-- Name: votos votos_pkey; Type: CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.votos
    ADD CONSTRAINT votos_pkey PRIMARY KEY (id);


--
-- Name: idx_enquetes_ativa; Type: INDEX; Schema: public; Owner: totem_usuario
--

CREATE INDEX idx_enquetes_ativa ON public.enquetes USING btree (ativa);


--
-- Name: idx_votos_data; Type: INDEX; Schema: public; Owner: totem_usuario
--

CREATE INDEX idx_votos_data ON public.votos USING btree (data_voto);


--
-- Name: idx_votos_enquete; Type: INDEX; Schema: public; Owner: totem_usuario
--

CREATE INDEX idx_votos_enquete ON public.votos USING btree (enquete_id);


--
-- Name: atendimentos atendimentos_id_senha_fkey; Type: FK CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.atendimentos
    ADD CONSTRAINT atendimentos_id_senha_fkey FOREIGN KEY (id_senha) REFERENCES public.senhas(id_senha);


--
-- Name: votos votos_aluno_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.votos
    ADD CONSTRAINT votos_aluno_id_fkey FOREIGN KEY (aluno_id) REFERENCES public.alunos(id_aluno);


--
-- Name: votos votos_candidato_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.votos
    ADD CONSTRAINT votos_candidato_id_fkey FOREIGN KEY (candidato_id) REFERENCES public.candidatos(id_candidato);


--
-- Name: votos votos_enquete_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: totem_usuario
--

ALTER TABLE ONLY public.votos
    ADD CONSTRAINT votos_enquete_id_fkey FOREIGN KEY (enquete_id) REFERENCES public.enquetes(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict UB4GtSOR9R7qK77yjBTMNhCafxyHkB9ILOIOaablqJ2l3bfhC4ZLt7gEe9sAc5k
