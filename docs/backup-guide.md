# 백업 및 복구 가이드

## 💾 자동 백업 시스템

### 1. 백업 전략

#### 1.1 백업 유형

**자동 백업**
- 설정된 주기에 따라 자동 실행
- 사용자 개입 불필요
- 백그라운드에서 조용히 실행

**수동 백업**
- 사용자가 원할 때 즉시 실행
- 중요한 작업 전후에 권장
- 설명 메모 추가 가능

**증분 백업** (향후 구현)
- 변경된 부분만 백업
- 저장 공간 절약
- 빠른 백업 속도

#### 1.2 백업 주기 옵션

```python
# backend/backup/scheduler.py
from enum import Enum

class BackupFrequency(Enum):
    REALTIME = "realtime"    # 변경 시마다 (고급 사용자용)
    HOURLY = "hourly"        # 매 시간
    DAILY = "daily"          # 매일 (기본값) ⭐
    WEEKLY = "weekly"        # 매주
    MONTHLY = "monthly"      # 매월
    MANUAL = "manual"        # 수동만
```

#### 1.3 백업 보관 정책 (GFS: Grandfather-Father-Son)

```
일일 백업 (Son)     → 최근 7일 보관
주간 백업 (Father)  → 최근 4주 보관
월간 백업 (Grandfather) → 최근 12개월 보관
연간 백업           → 영구 보관 (선택사항)
```

### 2. 백업 구현

#### 2.1 백업 스케줄러

```python
# backend/backup/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

class BackupScheduler:
    """백업 스케줄러"""
    
    def __init__(self, backup_manager):
        self.scheduler = BackgroundScheduler()
        self.backup_manager = backup_manager
        self.logger = logging.getLogger(__name__)
    
    def start(self, frequency: BackupFrequency):
        """백업 스케줄 시작"""
        if frequency == BackupFrequency.DAILY:
            # 매일 오전 9시
            trigger = CronTrigger(hour=9, minute=0)
        elif frequency == BackupFrequency.HOURLY:
            # 매 시간
            trigger = CronTrigger(minute=0)
        elif frequency == BackupFrequency.WEEKLY:
            # 매주 일요일 오전 9시
            trigger = CronTrigger(day_of_week='sun', hour=9, minute=0)
        elif frequency == BackupFrequency.MONTHLY:
            # 매월 1일 오전 9시
            trigger = CronTrigger(day=1, hour=9, minute=0)
        else:
            return  # MANUAL 또는 REALTIME
        
        self.scheduler.add_job(
            self._perform_backup,
            trigger=trigger,
            id='auto_backup',
            replace_existing=True
        )
        self.scheduler.start()
        self.logger.info(f"백업 스케줄 시작: {frequency.value}")
    
    def _perform_backup(self):
        """백업 실행"""
        try:
            self.backup_manager.create_backup(auto=True)
            self.logger.info("자동 백업 완료")
        except Exception as e:
            self.logger.error(f"자동 백업 실패: {e}")
    
    def stop(self):
        """백업 스케줄 중지"""
        self.scheduler.shutdown()
```

#### 2.2 백업 매니저

```python
# backend/backup/manager.py
import os
import shutil
import gzip
from datetime import datetime
from pathlib import Path
from typing import Optional
from ..security.encryption import FileEncryption

class BackupManager:
    """백업 관리자"""
    
    def __init__(self, db_path: str, backup_dir: str, password: str):
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.password = password
        
        # 백업 디렉토리 생성
        self.auto_dir = self.backup_dir / 'auto'
        self.manual_dir = self.backup_dir / 'manual'
        self.auto_dir.mkdir(parents=True, exist_ok=True)
        self.manual_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, auto: bool = True, description: str = "") -> str:
        """백업 생성"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        if auto:
            backup_name = f"backup_{timestamp}"
            backup_dir = self.auto_dir
        else:
            backup_name = f"{description}_{timestamp}" if description else f"manual_{timestamp}"
            backup_dir = self.manual_dir
        
        # 1. 데이터베이스 복사
        temp_db = backup_dir / f"{backup_name}.db"
        shutil.copy2(self.db_path, temp_db)
        
        # 2. 압축
        compressed_file = backup_dir / f"{backup_name}.db.gz"
        with open(temp_db, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 임시 파일 삭제
        temp_db.unlink()
        
        # 3. 암호화
        encrypted_file = FileEncryption.encrypt_file(
            str(compressed_file),
            self.password
        )
        
        # 압축 파일 삭제
        compressed_file.unlink()
        
        # 4. 메타데이터 저장
        self._save_metadata(encrypted_file, description)
        
        return encrypted_file
    
    def restore_backup(self, backup_file: str, output_path: str):
        """백업 복구"""
        # 1. 현재 데이터베이스 백업 (안전장치)
        safety_backup = self.create_backup(auto=False, description="before_restore")
        
        try:
            # 2. 복호화
            temp_compressed = backup_file.replace('.enc', '')
            FileEncryption.decrypt_file(backup_file, self.password, temp_compressed)
            
            # 3. 압축 해제
            temp_db = temp_compressed.replace('.gz', '')
            with gzip.open(temp_compressed, 'rb') as f_in:
                with open(temp_db, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 4. 데이터베이스 복원
            shutil.copy2(temp_db, output_path)
            
            # 5. 임시 파일 삭제
            os.unlink(temp_compressed)
            os.unlink(temp_db)
            
            # 6. 무결성 검증
            if not self._verify_database(output_path):
                raise ValueError("복구된 데이터베이스가 손상되었습니다")
            
            return True
        except Exception as e:
            # 복구 실패 시 안전 백업으로 롤백
            self.restore_backup(safety_backup, output_path)
            raise e
    
    def list_backups(self, auto: bool = None) -> list:
        """백업 목록 조회"""
        backups = []
        
        dirs = []
        if auto is None:
            dirs = [self.auto_dir, self.manual_dir]
        elif auto:
            dirs = [self.auto_dir]
        else:
            dirs = [self.manual_dir]
        
        for backup_dir in dirs:
            for file in backup_dir.glob('*.enc'):
                metadata = self._load_metadata(str(file))
                backups.append({
                    'path': str(file),
                    'name': file.stem,
                    'type': 'auto' if backup_dir == self.auto_dir else 'manual',
                    'size': file.stat().st_size,
                    'created': datetime.fromtimestamp(file.stat().st_ctime),
                    'description': metadata.get('description', ''),
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def cleanup_old_backups(self):
        """오래된 백업 정리 (GFS 정책)"""
        now = datetime.now()
        
        for backup in self.list_backups(auto=True):
            age_days = (now - backup['created']).days
            
            # 일일 백업: 7일 이상 된 것 삭제
            if age_days > 7:
                # 주간 백업으로 승격 (일요일 백업만)
                if backup['created'].weekday() == 6:  # 일요일
                    if age_days > 28:  # 4주 이상
                        # 월간 백업으로 승격 (매월 1일 백업만)
                        if backup['created'].day == 1:
                            if age_days > 365:  # 1년 이상
                                os.unlink(backup['path'])
                        else:
                            os.unlink(backup['path'])
                else:
                    os.unlink(backup['path'])
    
    def _save_metadata(self, backup_file: str, description: str):
        """백업 메타데이터 저장"""
        metadata_file = f"{backup_file}.meta"
        metadata = {
            'created': datetime.now().isoformat(),
            'description': description,
            'db_path': self.db_path,
        }
        
        import json
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
    
    def _load_metadata(self, backup_file: str) -> dict:
        """백업 메타데이터 로드"""
        metadata_file = f"{backup_file}.meta"
        if not os.path.exists(metadata_file):
            return {}
        
        import json
        with open(metadata_file, 'r') as f:
            return json.load(f)
    
    def _verify_database(self, db_path: str) -> bool:
        """데이터베이스 무결성 검증"""
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()
            return result[0] == 'ok'
        except Exception:
            return False
```

### 3. 백업 UI

#### 3.1 백업 설정 화면

```typescript
// frontend/src/components/Settings/BackupSettings.tsx
import React, { useState } from 'react';
import { 
  Box, 
  Switch, 
  Select, 
  MenuItem, 
  FormControlLabel,
  TextField,
  Button 
} from '@mui/material';

interface BackupSettings {
  autoBackupEnabled: boolean;
  frequency: 'hourly' | 'daily' | 'weekly' | 'monthly';
  time: string;
  encryptBackups: boolean;
  retentionDays: number;
}

export const BackupSettingsPanel: React.FC = () => {
  const [settings, setSettings] = useState<BackupSettings>({
    autoBackupEnabled: true,
    frequency: 'daily',
    time: '09:00',
    encryptBackups: true,
    retentionDays: 30,
  });
  
  const handleSave = async () => {
    await fetch('http://localhost:8000/api/backup/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings),
    });
  };
  
  return (
    <Box>
      <FormControlLabel
        control={
          <Switch
            checked={settings.autoBackupEnabled}
            onChange={(e) => setSettings({
              ...settings,
              autoBackupEnabled: e.target.checked
            })}
          />
        }
        label="자동 백업 활성화"
      />
      
      <Select
        value={settings.frequency}
        onChange={(e) => setSettings({
          ...settings,
          frequency: e.target.value as any
        })}
      >
        <MenuItem value="hourly">매 시간</MenuItem>
        <MenuItem value="daily">매일</MenuItem>
        <MenuItem value="weekly">매주</MenuItem>
        <MenuItem value="monthly">매월</MenuItem>
      </Select>
      
      <TextField
        type="time"
        value={settings.time}
        onChange={(e) => setSettings({
          ...settings,
          time: e.target.value
        })}
      />
      
      <Button onClick={handleSave}>저장</Button>
    </Box>
  );
};
```

### 4. 복구 프로세스

#### 4.1 복구 단계

```
1. 백업 파일 선택
   ↓
2. 현재 데이터 안전 백업
   ↓
3. 복호화
   ↓
4. 압축 해제
   ↓
5. 데이터베이스 복원
   ↓
6. 무결성 검증
   ↓
7. 완료 또는 롤백
```

#### 4.2 복구 UI

```typescript
// frontend/src/components/Backup/RestoreDialog.tsx
import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, List, ListItem } from '@mui/material';

interface Backup {
  path: string;
  name: string;
  type: 'auto' | 'manual';
  size: number;
  created: string;
  description: string;
}

export const RestoreDialog: React.FC = () => {
  const [backups, setBackups] = useState<Backup[]>([]);
  
  const handleRestore = async (backup: Backup) => {
    if (!confirm(`"${backup.name}" 백업으로 복구하시겠습니까?\n현재 데이터는 자동으로 백업됩니다.`)) {
      return;
    }
    
    try {
      const response = await fetch('http://localhost:8000/api/backup/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ backup_path: backup.path }),
      });
      
      if (response.ok) {
        alert('복구가 완료되었습니다. 애플리케이션을 재시작합니다.');
        // 재시작 로직
      }
    } catch (error) {
      alert('복구 실패: ' + error);
    }
  };
  
  return (
    <Dialog open>
      <DialogTitle>백업 복구</DialogTitle>
      <DialogContent>
        <List>
          {backups.map(backup => (
            <ListItem key={backup.path} onClick={() => handleRestore(backup)}>
              {backup.name} - {backup.created}
            </ListItem>
          ))}
        </List>
      </DialogContent>
    </Dialog>
  );
};
```

### 5. 백업 모범 사례

#### 5.1 3-2-1 백업 규칙
```
3개의 복사본: 원본 + 백업 2개
2개의 다른 매체: 로컬 디스크 + 외장 하드
1개의 오프사이트: 클라우드 또는 다른 장소
```

#### 5.2 백업 체크리스트
- [ ] 자동 백업 활성화
- [ ] 백업 암호화 활성화
- [ ] 정기적인 복구 테스트
- [ ] 백업 파일 외부 저장
- [ ] 백업 로그 확인

---

**문서 버전**: 1.0  
**최종 수정일**: 2024-01-20

