use std::process::{Command, Child};
use std::sync::Mutex;
use tauri::{Manager, State, WebviewWindow, Emitter};

struct BackendProcess(Mutex<Option<Child>>);

fn emit_setup_progress(window: &WebviewWindow, message: &str) {
  let _ = window.emit("setup-progress", message);
  println!("{}", message);
}

#[tauri::command]
fn start_backend_setup(backend_state: State<BackendProcess>, window: WebviewWindow) -> Result<String, String> {
  // 백엔드가 이미 실행 중인지 확인
  if backend_state.0.lock().unwrap().is_some() {
    return Ok("백엔드가 이미 실행 중입니다.".to_string());
  }

  // 백엔드 시작 (설치 진행 상황 전달)
  let new_process = start_backend_with_progress(&window);
  *backend_state.0.lock().unwrap() = new_process;

  if backend_state.0.lock().unwrap().is_some() {
    Ok("백엔드 설치 및 시작이 완료되었습니다.".to_string())
  } else {
    Err("백엔드 시작에 실패했습니다.".to_string())
  }
}

#[tauri::command]
fn restart_backend(backend_state: State<BackendProcess>, window: WebviewWindow) -> Result<String, String> {
  // 기존 백엔드 프로세스 종료
  if let Some(backend) = backend_state.0.lock().unwrap().as_mut() {
    let _ = backend.kill();
  }

  // 새 백엔드 프로세스 시작 (설치 진행 상황 전달)
  let new_process = start_backend_with_progress(&window);
  *backend_state.0.lock().unwrap() = new_process;

  if backend_state.0.lock().unwrap().is_some() {
    Ok("백엔드가 성공적으로 재시작되었습니다.".to_string())
  } else {
    Err("백엔드 재시작에 실패했습니다.".to_string())
  }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      // 빈 프로세스로 초기화 (프론트엔드에서 start_backend_setup 호출 시 시작됨)
      app.manage(BackendProcess(Mutex::new(None)));

      Ok(())
    })
    .invoke_handler(tauri::generate_handler![start_backend_setup, restart_backend])
    .on_window_event(|window, event| {
      if let tauri::WindowEvent::Destroyed = event {
        // 윈도우 종료 시 백엔드 프로세스도 종료
        if let Some(backend) = window.state::<BackendProcess>().0.lock().unwrap().as_mut() {
          let _ = backend.kill();
        }
      }
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}

fn start_backend_with_progress(window: &WebviewWindow) -> Option<Child> {
  emit_setup_progress(window, "🚀 백엔드 초기화 중...");

  // 백엔드 디렉토리 경로 찾기
  let backend_path = if cfg!(debug_assertions) {
    // 개발 모드: 프로젝트 루트의 backend 폴더
    std::env::current_dir()
      .ok()?
      .parent()?
      .parent()?
      .join("backend")
  } else {
    // 프로덕션 모드: 실행 파일 근처의 backend 폴더
    std::env::current_exe()
      .ok()?
      .parent()?
      .join("backend")
  };

  emit_setup_progress(window, &format!("📁 백엔드 경로: {:?}", backend_path));

  // Python 실행 파일 찾기
  let python_cmd = if cfg!(target_os = "windows") {
    "python"
  } else {
    "python3"
  };

  // 가상환경의 Python 사용 (있는 경우)
  let venv_python = if cfg!(target_os = "windows") {
    backend_path.join("venv").join("Scripts").join("python.exe")
  } else {
    // macOS/Linux: python3 심볼릭 링크 사용
    backend_path.join("venv").join("bin").join("python3")
  };

  let python_executable = if venv_python.exists() {
    venv_python.to_str()?.to_string()
  } else {
    python_cmd.to_string()
  };

  emit_setup_progress(window, &format!("🐍 Python: {}", python_executable));

  // 가상환경이 없으면 생성
  if !venv_python.exists() {
    emit_setup_progress(window, "📦 가상환경 생성 중...");
    let venv_result = Command::new(python_cmd)
      .args(&["-m", "venv", "venv"])
      .current_dir(&backend_path)
      .output();

    match venv_result {
      Ok(output) => {
        if output.status.success() {
          emit_setup_progress(window, "✅ 가상환경 생성 완료");
        } else {
          emit_setup_progress(window, &format!("❌ 가상환경 생성 실패: {:?}", String::from_utf8_lossy(&output.stderr)));
        }
      }
      Err(e) => {
        emit_setup_progress(window, &format!("❌ 가상환경 생성 실패: {}", e));
      }
    }
  } else {
    emit_setup_progress(window, "✅ 가상환경 확인됨");
  }

  // pip 업그레이드 및 의존성 설치
  let pip_executable = if cfg!(target_os = "windows") {
    backend_path.join("venv").join("Scripts").join("pip.exe")
  } else {
    backend_path.join("venv").join("bin").join("pip")
  };

  if pip_executable.exists() {
    emit_setup_progress(window, "📦 의존성 확인 중...");

    // pip 업그레이드
    emit_setup_progress(window, "⬆️  pip 업그레이드 중...");
    let _ = Command::new(&pip_executable)
      .args(&["install", "--upgrade", "pip", "-q"])
      .current_dir(&backend_path)
      .output();

    // requirements.txt 설치
    let requirements_path = backend_path.join("requirements.txt");
    if requirements_path.exists() {
      emit_setup_progress(window, "📥 Python 라이브러리 설치 중... (최초 실행 시 시간이 걸릴 수 있습니다)");
      let install_result = Command::new(&pip_executable)
        .args(&["install", "-r", "requirements.txt", "-q"])
        .current_dir(&backend_path)
        .output();

      match install_result {
        Ok(output) => {
          if output.status.success() {
            emit_setup_progress(window, "✅ 의존성 설치 완료");
          } else {
            emit_setup_progress(window, &format!("⚠️  의존성 설치 경고: {:?}", String::from_utf8_lossy(&output.stderr)));
          }
        }
        Err(e) => {
          emit_setup_progress(window, &format!("❌ 의존성 설치 실패: {}", e));
        }
      }
    }
  }

  // 백엔드 서버 시작
  emit_setup_progress(window, "🚀 백엔드 서버 시작 중...");
  let child = Command::new(python_executable)
    .arg("main.py")
    .current_dir(&backend_path)
    .spawn();

  match child {
    Ok(process) => {
      emit_setup_progress(window, &format!("✅ 백엔드 시작 완료 (PID: {})", process.id()));
      Some(process)
    }
    Err(e) => {
      emit_setup_progress(window, &format!("❌ 백엔드 시작 실패: {}", e));
      None
    }
  }
}
