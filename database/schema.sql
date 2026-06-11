-- ============================================================
-- Teacher Attrition EWS — MySQL Schema
-- Authors: Florence Kabeya  | ALU
-- Run this script to initialise the database manually.
-- SQLAlchemy ORM will also auto-create these via create_tables().
-- ============================================================

CREATE DATABASE IF NOT EXISTS teacher_ews
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE teacher_ews;

-- ── schools ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS schools (
  school_code   VARCHAR(20)  NOT NULL PRIMARY KEY,
  name          VARCHAR(200) NOT NULL,
  district      VARCHAR(100) NOT NULL,
  province      VARCHAR(100) NOT NULL,
  school_type   VARCHAR(50),
  is_rural      TINYINT(1)   DEFAULT 1,
  created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_district (district),
  INDEX idx_province (province)
) ENGINE=InnoDB;

-- ── teacher_records ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teacher_records (
  record_id       INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  school_code     VARCHAR(20)  NOT NULL,
  year            INT          NOT NULL,
  teacher_count   INT,
  qualified_count INT,
  ptr             FLOAT,
  enrolment       INT,
  attrition_est   INT,
  created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (school_code) REFERENCES schools(school_code) ON DELETE CASCADE,
  INDEX idx_school_year (school_code, year)
) ENGINE=InnoDB;

-- ── ml_models ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ml_models (
  model_version  VARCHAR(50)  NOT NULL PRIMARY KEY,
  algorithm      VARCHAR(100) NOT NULL,
  f1_score       FLOAT,
  recall_score   FLOAT,
  auc_score      FLOAT,
  trained_at     DATETIME     DEFAULT CURRENT_TIMESTAMP,
  artefact_path  VARCHAR(500),
  is_active      TINYINT(1)   DEFAULT 0,
  notes          TEXT
) ENGINE=InnoDB;

-- ── risk_predictions ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS risk_predictions (
  prediction_id  INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  school_code    VARCHAR(20)  NOT NULL,
  model_version  VARCHAR(50)  NOT NULL,
  risk_score     FLOAT        NOT NULL,
  risk_label     ENUM('high_risk', 'not_at_risk') NOT NULL,
  shap_json      TEXT,
  confidence_pct FLOAT,
  predicted_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (school_code)   REFERENCES schools(school_code)  ON DELETE CASCADE,
  FOREIGN KEY (model_version) REFERENCES ml_models(model_version) ON DELETE CASCADE,
  INDEX idx_school_predicted (school_code, predicted_at)
) ENGINE=InnoDB;

-- ── users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  user_id       INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username      VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('district_officer', 'data_admin', 'viewer') DEFAULT 'viewer',
  province      VARCHAR(100),
  created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_username (username)
) ENGINE=InnoDB;

-- ── Seed: active model record ─────────────────────────────────
INSERT IGNORE INTO ml_models (model_version, algorithm, f1_score, recall_score, auc_score, is_active, notes)
VALUES ('xgb_v1.0', 'XGBoost (RandomizedSearchCV tuned)', NULL, NULL, NULL, 1,
        'Trained on MoE Bulletin 2022 — 10 provinces, primary + secondary, 2020-2022');
