import React, { useEffect, useState } from 'react';
import { Card, Table, Button, Space, message, Spin, Select, Statistic, Row, Col } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { sampleApi } from '../api';

interface SampleStudent {
  학년: number;
  반: number;
  번호: number;
  이름: string;
  성별: string;
  성적: string;
  생활태도: string;
  교우관계: string;
  특기: string;
  쌍둥이: string;
  함께: string;
  분리: string;
  특별관리: string;
  비고: string;
}

const SamplePreview: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [students, setStudents] = useState<SampleStudent[]>([]);
  const [selectedClass, setSelectedClass] = useState<number | 'all'>('all');

  useEffect(() => {
    loadSampleData();
  }, []);

  const loadSampleData = async () => {
    setLoading(true);
    try {
      const response = await sampleApi.downloadExcel();
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });

      // Excel 파일을 읽어서 JSON으로 변환
      const XLSX = await import('xlsx');
      const arrayBuffer = await blob.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer, { type: 'array' });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json<SampleStudent>(worksheet);

      setStudents(jsonData);
    } catch (error) {
      message.error('샘플 데이터 로드에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 반별 필터링된 학생 목록
  const filteredStudents = selectedClass === 'all'
    ? students
    : students.filter(s => s.반 === selectedClass);

  // 반 목록 생성 (1~7반)
  const classOptions = [
    { label: '전체', value: 'all' as const },
    ...Array.from({ length: 7 }, (_, i) => ({
      label: `${i + 1}반`,
      value: i + 1
    }))
  ];

  // 통계 계산
  const stats = {
    total: filteredStudents.length,
    male: filteredStudents.filter(s => s.성별 === '남').length,
    female: filteredStudents.filter(s => s.성별 === '여').length,
    twins: filteredStudents.filter(s => s.쌍둥이).length,
    together: filteredStudents.filter(s => s.함께).length,
    separate: filteredStudents.filter(s => s.분리).length,
    special: filteredStudents.filter(s => s.특별관리).length,
  };

  const columns = [
    { title: '학년', dataIndex: '학년', key: '학년', width: 60 },
    { title: '반', dataIndex: '반', key: '반', width: 60 },
    { title: '번호', dataIndex: '번호', key: '번호', width: 60 },
    { title: '이름', dataIndex: '이름', key: '이름', width: 100 },
    { title: '성별', dataIndex: '성별', key: '성별', width: 60 },
    { title: '성적', dataIndex: '성적', key: '성적', width: 60 },
    { title: '생활태도', dataIndex: '생활태도', key: '생활태도', width: 80 },
    { title: '교우관계', dataIndex: '교우관계', key: '교우관계', width: 80 },
    { title: '특기', dataIndex: '특기', key: '특기', width: 100 },
    { title: '쌍둥이', dataIndex: '쌍둥이', key: '쌍둥이', width: 150 },
    { title: '함께', dataIndex: '함께', key: '함께', width: 150 },
    { title: '분리', dataIndex: '분리', key: '분리', width: 150 },
    { title: '특별관리', dataIndex: '특별관리', key: '특별관리', width: 80 },
    { title: '비고', dataIndex: '비고', key: '비고', width: 120 },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card
        title="샘플 데이터 미리보기"
        extra={
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')}>
            돌아가기
          </Button>
        }
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>샘플 데이터 로딩 중...</p>
          </div>
        ) : (
          <>
            {/* 반 선택 드롭다운 */}
            <Space style={{ marginBottom: 16 }}>
              <span>반 선택:</span>
              <Select
                value={selectedClass}
                onChange={setSelectedClass}
                options={classOptions}
                style={{ width: 120 }}
              />
            </Space>

            {/* 통계 정보 */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={4}>
                <Statistic title="총 학생" value={stats.total} suffix="명" />
              </Col>
              <Col span={4}>
                <Statistic title="남학생" value={stats.male} suffix="명" />
              </Col>
              <Col span={4}>
                <Statistic title="여학생" value={stats.female} suffix="명" />
              </Col>
              <Col span={4}>
                <Statistic title="쌍둥이" value={stats.twins} suffix="명" />
              </Col>
              <Col span={4}>
                <Statistic title="함께 배치" value={stats.together} suffix="명" />
              </Col>
              <Col span={4}>
                <Statistic title="분리 배치" value={stats.separate} suffix="명" />
              </Col>
            </Row>

            {/* 학생 목록 테이블 */}
            <Table
              columns={columns}
              dataSource={filteredStudents}
              rowKey={(record, index) => `${record.학년}-${record.반}-${record.번호}-${index}`}
              pagination={{ pageSize: 25, showSizeChanger: true, pageSizeOptions: ['10', '25', '50', '100'] }}
              scroll={{ x: 1500 }}
              size="small"
            />
          </>
        )}
      </Card>
    </div>
  );
};

export default SamplePreview;

