import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider, message } from 'antd';
import koKR from 'antd/locale/ko_KR';
import { Layout } from './components/Layout';
import { SetupProgress } from './components/SetupProgress';
import { Home } from './pages/Home';
import { Students } from './pages/Students';
import { Rules } from './pages/Rules';
import { Assignments } from './pages/Assignments';
import SamplePreview from './pages/SamplePreview';
import { useStore } from './store/useStore';
import { schoolApi } from './api';
import { listen } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';

function App() {
  const { setCurrentSchool } = useStore();
  const [setupInProgress, setSetupInProgress] = useState(true);

  useEffect(() => {
    console.log('App: Component mounted, starting backend setup');

    // 설치 진행 상황 리스닝
    const setupListener = async () => {
      const unlisten = await listen<string>('setup-progress', (event) => {
        console.log('App: Received setup-progress event:', event.payload);
        if (event.payload.includes('백엔드 시작 완료')) {
          console.log('App: Backend started, will close setup modal in 1 second');
          // 백엔드 시작 완료 후 1초 대기 후 설정 완료
          setTimeout(() => {
            console.log('App: Closing setup modal');
            setSetupInProgress(false);
          }, 1000);
        }
      });

      // 이벤트 리스너 등록 후 백엔드 설치 시작
      console.log('App: Event listener registered, invoking start_backend_setup');
      try {
        await invoke('start_backend_setup');
        console.log('App: start_backend_setup completed');
      } catch (error) {
        console.error('App: start_backend_setup failed:', error);
        message.error('백엔드 시작에 실패했습니다.');
        setSetupInProgress(false);
      }

      return unlisten;
    };

    const unlistenPromise = setupListener();

    return () => {
      unlistenPromise.then((fn) => fn());
    };
  }, []);

  useEffect(() => {
    if (!setupInProgress) {
      // 앱 시작 시 학교 정보 로드 또는 생성
      const initSchool = async () => {
        try {
          const response = await schoolApi.getAll();
          if (response.data.length > 0) {
            setCurrentSchool(response.data[0]);
          } else {
            // 기본 학교 생성
            const newSchool = await schoolApi.create({
              name: '우리 학교',
              custom_field_definitions: [],
              settings: {},
            });
            setCurrentSchool(newSchool.data);
          }
        } catch (error) {
          console.error('Failed to initialize school:', error);
          message.warning('백엔드 서버 연결을 확인해주세요.');
        }
      };

      // 백엔드 시작 대기 후 초기화
      setTimeout(initSchool, 1000);
    }
  }, [setupInProgress]);

  return (
    <ConfigProvider locale={koKR}>
      <SetupProgress visible={setupInProgress} />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="students" element={<Students />} />
            <Route path="rules" element={<Rules />} />
            <Route path="assignments" element={<Assignments />} />
            <Route path="sample-preview" element={<SamplePreview />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
