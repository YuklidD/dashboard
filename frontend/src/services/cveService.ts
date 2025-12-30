import api from './api';

export interface CVEMetric {
    baseScore: number;
    severity: string;
}

export interface CVEItem {
    id: string;
    sourceIdentifier: string;
    published: string;
    lastModified: string;
    vulnStatus: string;
    description: string;
    metrics: CVEMetric | null;
}

export interface CVELiistResponse {
    timestamp: string;
    totalResults: number;
    cves: CVEItem[];
}

export const cveService = {
    getRecentCVEs: async (days: number = 7, limit: number = 20): Promise<CVELiistResponse> => {
        const response = await api.get<CVELiistResponse>('/cves/', {
            params: { days, limit }
        });
        return response.data;
    }
};
