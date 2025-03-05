import React, { useState } from "react";
import axios from "axios";
import { saveAs } from "file-saver";
import * as XLSX from "xlsx";

const SearchVolumeTable = () => {
  const [keywords, setKeywords] = useState("");
  const [data, setData] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "asc" });

  // ✅ API 호출하여 검색량 데이터 가져오기
  const fetchSearchVolume = async () => {
    if (!keywords.trim()) return alert("검색어를 입력하세요.");
    
    try {
      const response = await axios.post("http://localhost:5000/api/search-volume", {
        keywords
      });
      const newData = response.data.map((item, index) => ({
        id: index + 1,
        keyword: item.keyword,
        pc_search: item.pc_search,
        mobile_search: item.mobile_search,
        total: item.pc_search + item.mobile_search
      }));
      setData(newData);
    } catch (error) {
      console.error("API 요청 실패:", error);
      alert("데이터를 불러오는데 실패했습니다.");
    }
  };

  // ✅ 정렬 기능
  const sortTable = (key) => {
    let direction = "asc";
    if (sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    const sortedData = [...data].sort((a, b) => {
      if (a[key] < b[key]) return direction === "asc" ? -1 : 1;
      if (a[key] > b[key]) return direction === "asc" ? 1 : -1;
      return 0;
    });

    setSortConfig({ key, direction });
    setData(sortedData);
  };

  // ✅ 개별 행 삭제
  const deleteRow = (id) => {
    setData(data.filter(row => row.id !== id));
  };

  // ✅ 엑셀 다운로드
  const downloadExcel = () => {
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "검색량 데이터");
    const excelBuffer = XLSX.write(wb, { bookType: "xlsx", type: "array" });
    const dataBlob = new Blob([excelBuffer], { type: "application/octet-stream" });
    saveAs(dataBlob, "검색량_데이터.xlsx");
  };

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "auto" }}>
      <h2>📊 키워드 검색량 조회</h2>
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <input
          type="text"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="예: 청소년샴푸, 임산부샴푸"
          style={{ flex: 1, padding: "10px", fontSize: "16px" }}
        />
        <button onClick={fetchSearchVolume} style={{ padding: "10px 15px", fontSize: "16px", cursor: "pointer" }}>
          검색
        </button>
      </div>

      {data.length > 0 && (
        <>
          <table border="1" style={{ width: "100%", borderCollapse: "collapse", textAlign: "center" }}>
            <thead>
              <tr>
                <th>연번</th>
                <th>키워드</th>
                <th onClick={() => sortTable("pc_search")} style={{ cursor: "pointer" }}>PC 검색량 ⬍</th>
                <th onClick={() => sortTable("mobile_search")} style={{ cursor: "pointer" }}>모바일 검색량 ⬍</th>
                <th onClick={() => sortTable("total")} style={{ cursor: "pointer" }}>합 ⬍</th>
                <th>삭제</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={row.id}>
                  <td>{index + 1}</td>
                  <td>{row.keyword}</td>
                  <td>{row.pc_search.toLocaleString()}</td>
                  <td>{row.mobile_search.toLocaleString()}</td>
                  <td>{row.total.toLocaleString()}</td>
                  <td>
                    <button onClick={() => deleteRow(row.id)} style={{ color: "red", cursor: "pointer" }}>❌</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button onClick={downloadExcel} style={{ marginTop: "15px", padding: "10px", fontSize: "16px", cursor: "pointer" }}>
            📥 엑셀 다운로드
          </button>
        </>
      )}
    </div>
  );
};

export default SearchVolumeTable;
