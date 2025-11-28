-- Insert Dummy Data for Face Registration Testing
USE `e-learn`;

-- Insert dummy face registrations using existing mahasiswa NIMs

INSERT INTO face_registrations (nim, embedding_filename, registration_date, verification_count, failed_attempts, is_active)
VALUES 
    ('E41253310', 'mahasiswa_tif_1.pkl', NOW() - INTERVAL 7 DAY, 25, 0, TRUE),
    ('E41253311', 'mahasiswa_tif_2.pkl', NOW() - INTERVAL 5 DAY, 18, 0, TRUE),
    ('E51253310', 'mahasiswa_mif_1.pkl', NOW() - INTERVAL 3 DAY, 12, 2, TRUE)
ON DUPLICATE KEY UPDATE
    embedding_filename = VALUES(embedding_filename),
    registration_date = VALUES(registration_date),
    verification_count = VALUES(verification_count),
    failed_attempts = VALUES(failed_attempts),
    is_active = VALUES(is_active);

-- Update some with last_verified dates
UPDATE face_registrations 
SET last_verified = NOW() - INTERVAL 2 HOUR 
WHERE nim = 'E41253310';

UPDATE face_registrations 
SET last_verified = NOW() - INTERVAL 5 HOUR 
WHERE nim = 'E41253311';

UPDATE face_registrations 
SET last_verified = NOW() - INTERVAL 1 DAY 
WHERE nim = 'E51253310';

-- Insert dummy presensi with face verification data
-- Get id_mahasiswa first, then update presensi
UPDATE presensi p
JOIN mahasiswa m ON p.id_mahasiswa = m.id_mahasiswa
SET 
    p.verified_by_face = TRUE,
    p.face_match_confidence = 95.50,
    p.verification_photo_path = 'uploads/face_verification/E41253310_20250127_080000.jpg',
    p.device_info = 'Samsung Galaxy S21 (Android 13)',
    p.app_version = '1.0.5'
WHERE m.nim = 'E41253310'
LIMIT 1;

UPDATE presensi p
JOIN mahasiswa m ON p.id_mahasiswa = m.id_mahasiswa
SET 
    p.verified_by_face = TRUE,
    p.face_match_confidence = 89.75,
    p.verification_photo_path = 'uploads/face_verification/E41253311_20250127_080015.jpg',
    p.device_info = 'Xiaomi Redmi Note 10 (Android 12)',
    p.app_version = '1.0.5'
WHERE m.nim = 'E41253311'
LIMIT 1;

SELECT 'Dummy data inserted successfully!' AS Status;

-- Check the data
SELECT 
    fr.nim,
    m.nama,
    fr.embedding_filename,
    fr.registration_date,
    fr.last_verified,
    fr.verification_count,
    fr.failed_attempts,
    fr.is_active
FROM face_registrations fr
JOIN mahasiswa m ON fr.nim = m.nim
ORDER BY fr.registration_date DESC;
