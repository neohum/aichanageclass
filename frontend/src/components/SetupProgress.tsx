import { useEffect, useState } from 'react';
import { Modal, Progress, List, Typography } from 'antd';
import { listen } from '@tauri-apps/api/event';

const { Text } = Typography;

interface SetupProgressProps {
  visible: boolean;
}

export const SetupProgress = ({ visible }: SetupProgressProps) => {
  const [messages, setMessages] = useState<string[]>([]);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    console.log('SetupProgress: Setting up event listener');

    const unlisten = listen<string>('setup-progress', (event) => {
      const message = event.payload;
      console.log('SetupProgress: Received message:', message);
      setMessages((prev) => [...prev, message]);

      // 진행률 계산 (간단한 추정)
      if (message.includes('초기화')) setProgress(10);
      else if (message.includes('가상환경 생성')) setProgress(30);
      else if (message.includes('가상환경 확인')) setProgress(40);
      else if (message.includes('pip 업그레이드')) setProgress(50);
      else if (message.includes('라이브러리 설치')) setProgress(60);
      else if (message.includes('의존성 설치 완료')) setProgress(90);
      else if (message.includes('백엔드 시작 완료')) setProgress(100);
    });

    return () => {
      console.log('SetupProgress: Cleaning up event listener');
      unlisten.then((fn) => fn());
    };
  }, []);

  return (
    <Modal
      title="초기 설정 중"
      open={visible}
      footer={null}
      closable={false}
      centered
      width={600}
    >
      <div style={{ padding: '20px 0' }}>
        <Progress percent={progress} status={progress === 100 ? 'success' : 'active'} />
        
        <div style={{ marginTop: 24, maxHeight: 300, overflowY: 'auto' }}>
          <List
            size="small"
            dataSource={messages}
            renderItem={(item) => (
              <List.Item>
                <Text style={{ fontSize: 12, fontFamily: 'monospace' }}>{item}</Text>
              </List.Item>
            )}
          />
        </div>

        {progress === 100 && (
          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <Text type="success">설정이 완료되었습니다! 잠시 후 앱이 시작됩니다...</Text>
          </div>
        )}
      </div>
    </Modal>
  );
};

