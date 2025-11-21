import { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Alert, Spin, Button, Space, Badge, Modal } from 'antd';
import { TeamOutlined, SettingOutlined, SolutionOutlined, ReloadOutlined, CheckCircleOutlined, CloseCircleOutlined, EyeOutlined, ExperimentOutlined, RocketOutlined } from '@ant-design/icons';
import { useStore } from '../store/useStore';
import { healthCheck, sampleApi, assignmentApi } from '../api';
import { invoke } from '@tauri-apps/api/core';
import { message } from 'antd';
import { useNavigate } from 'react-router-dom';

export const Home = () => {
  const { students, rules, assignments, currentSchool } = useStore();
  const navigate = useNavigate();
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [restarting, setRestarting] = useState(false);
  const [lastCheckTime, setLastCheckTime] = useState<Date>(new Date());
  const [loadingSample, setLoadingSample] = useState(false);
  const [testingAssignment, setTestingAssignment] = useState(false);

  const checkBackend = async () => {
    try {
      const response = await healthCheck();
      console.log('Health check success:', response.data);
      setBackendStatus('online');
      setLastCheckTime(new Date());
    } catch (error: any) {
      console.error('Health check failed:', error.message, error.response);
      setBackendStatus('offline');
      setLastCheckTime(new Date());
    }
  };

  useEffect(() => {
    checkBackend();
    const interval = setInterval(checkBackend, 3000); // 3초마다 체크

    return () => clearInterval(interval);
  }, []);

  const handleRestartBackend = async () => {
    try {
      setRestarting(true);
      setBackendStatus('checking');

      await invoke('restart_backend');

      message.success('백엔드가 재시작되었습니다.');

      // 재시작 후 3초 대기 후 상태 확인
      setTimeout(() => {
        checkBackend();
        setRestarting(false);
      }, 3000);
    } catch (error: any) {
      message.error(error || '백엔드 재시작에 실패했습니다.');
      setRestarting(false);
      setBackendStatus('offline');
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR');
  };

  // 샘플 데이터 미리보기
  const handleViewSample = () => {
    navigate('/sample-preview');
  };

  // 샘플 데이터 로드 및 테스트 실행
  const handleTestWithSample = async () => {
    if (!currentSchool) {
      message.error('학교 정보가 없습니다.');
      return;
    }

    Modal.confirm({
      title: '샘플 데이터로 테스트',
      content: '기존 학생 데이터가 삭제되고 샘플 데이터로 대체됩니다. 계속하시겠습니까?',
      okText: '확인',
      cancelText: '취소',
      onOk: async () => {
        try {
          setLoadingSample(true);
          setTestingAssignment(true);

          // 1. 샘플 데이터 로드
          message.loading({ content: '샘플 데이터 생성 중...', key: 'sample', duration: 0 });
          await sampleApi.loadSampleData(currentSchool.id);
          message.success({ content: '샘플 데이터가 로드되었습니다.', key: 'sample' });

          // 2. 샘플 규칙 생성
          message.loading({ content: '샘플 규칙 생성 중...', key: 'rules', duration: 0 });
          await sampleApi.createSampleRules(currentSchool.id);
          message.success({ content: '샘플 규칙이 생성되었습니다.', key: 'rules' });

          // 3. 반편성 실행
          message.loading({ content: '반편성 실행 중... (약 10초 소요)', key: 'assignment', duration: 0 });
          await assignmentApi.generate({
            school_id: currentSchool.id,
            grade: 3,
            year: new Date().getFullYear(),
            num_classes: 7,
            name: `샘플 반편성 ${new Date().toLocaleDateString()}`,
            method: 'genetic',
            iterations: 1000
          });
          message.success({ content: '반편성이 완료되었습니다!', key: 'assignment' });

          // 4. 반편성 페이지로 이동
          setTimeout(() => {
            navigate('/assignments');
          }, 1000);

        } catch (error: any) {
          message.error(error.response?.data?.detail || '테스트 실행에 실패했습니다.');
        } finally {
          setLoadingSample(false);
          setTestingAssignment(false);
        }
      }
    });
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>대시보드</h1>
      </div>

      {/* 백엔드 상태 카드 */}
      <Card
        title={
          <Space>
            <span>백엔드 서버 상태</span>
            <Badge
              status={backendStatus === 'online' ? 'success' : backendStatus === 'offline' ? 'error' : 'processing'}
              text={backendStatus === 'online' ? '정상 작동' : backendStatus === 'offline' ? '연결 실패' : '확인 중'}
            />
          </Space>
        }
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={handleRestartBackend}
            loading={restarting}
            disabled={backendStatus === 'checking'}
          >
            재시작
          </Button>
        }
        style={{ marginBottom: 24 }}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          {backendStatus === 'checking' && (
            <Alert
              message="백엔드 서버 연결 확인 중..."
              type="info"
              icon={<Spin />}
              showIcon
            />
          )}

          {backendStatus === 'offline' && (
            <Alert
              message="백엔드 서버 연결 실패"
              description="백엔드 서버가 시작되지 않았습니다. '재시작' 버튼을 클릭하여 다시 시도해주세요."
              type="error"
              icon={<CloseCircleOutlined />}
              showIcon
            />
          )}

          {backendStatus === 'online' && (
            <Alert
              message="백엔드 서버 정상 작동 중"
              description={`마지막 확인: ${formatTime(lastCheckTime)} (3초마다 자동 확인)`}
              type="success"
              icon={<CheckCircleOutlined />}
              showIcon
            />
          )}
        </Space>
      </Card>

      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="전체 학생 수"
              value={students.length}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="활성 규칙 수"
              value={rules.filter(r => r.is_active).length}
              prefix={<SettingOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="반편성 기록"
              value={assignments.length}
              prefix={<SolutionOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 샘플 데이터 테스트 카드 */}
      <Card
        title={
          <Space>
            <ExperimentOutlined />
            <span>샘플 데이터로 테스트하기</span>
          </Space>
        }
        style={{ marginTop: 24 }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Alert
            message="샘플 데이터 정보"
            description={
              <div>
                <p><strong>3학년 7개 반, 총 161명</strong></p>
                <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                  <li>반별 23명 (남녀 비율 다양: 10:13 ~ 16:7)</li>
                  <li>학생 번호: 남학생 1번~, 여학생 41번~</li>
                  <li>성적, 생활태도, 교우관계 데이터 포함</li>
                  <li>쌍둥이 5쌍 (10명) - 분리 배치</li>
                  <li>함께 배치 5쌍 (10명) - 같은 반 배치</li>
                  <li>분리 배치 5쌍 (10명) - 다른 반 배치</li>
                  <li>특별관리 학생 10명</li>
                  <li>자동 규칙 설정 (8개 규칙)</li>
                </ul>
              </div>
            }
            type="info"
            showIcon
          />

          <Space>
            <Button
              type="default"
              icon={<EyeOutlined />}
              onClick={handleViewSample}
            >
              샘플 데이터 미리보기
            </Button>

            <Button
              type="primary"
              icon={<RocketOutlined />}
              onClick={handleTestWithSample}
              loading={loadingSample || testingAssignment}
              disabled={!currentSchool}
            >
              {testingAssignment ? '반편성 실행 중...' : '샘플 데이터로 즉시 테스트'}
            </Button>
          </Space>

          {!currentSchool && (
            <Alert
              message="학교 정보가 없습니다. 먼저 학교를 선택해주세요."
              type="warning"
              showIcon
            />
          )}
        </Space>
      </Card>

      <Card title="시작하기" style={{ marginTop: 24 }}>
        <ol>
          <li>
            <strong>학생 관리</strong>: Excel 파일을 업로드하여 학생 데이터를 가져오세요.
          </li>
          <li>
            <strong>규칙 설정</strong>: 학교의 반편성 규칙을 정의하세요.
          </li>
          <li>
            <strong>반편성</strong>: 설정한 규칙에 따라 반편성을 실행하세요.
          </li>
        </ol>
      </Card>
    </div>
  );
};

