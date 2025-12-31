import { MapContainer, TileLayer, Popup, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default Leaflet icon not finding images in webpack/vite
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface AttackLocation {
    latitude: number;
    longitude: number;
    country: string;
    ip: string;
    type: string;
}

interface AttackMapProps {
    attacks: AttackLocation[];
}

const AttackMap = ({ attacks }: AttackMapProps) => {
    // Center of the map (roughly Europe/Africa for good initial view)
    const position: [number, number] = [20, 0];

    return (
        <div className="h-[400px] w-full rounded-md overflow-hidden border">
            <MapContainer center={position} zoom={2} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                {attacks.map((attack, i) => (
                    <CircleMarker
                        key={`${attack.ip}-${i}`}
                        center={[attack.latitude, attack.longitude]}
                        pathOptions={{ color: 'red', fillColor: '#ef4444', fillOpacity: 0.7 }}
                        radius={5}
                    >
                        <Popup>
                            <div className="text-sm font-mono">
                                <p><strong>IP:</strong> {attack.ip}</p>
                                <p><strong>Country:</strong> {attack.country}</p>
                                <p><strong>Type:</strong> {attack.type}</p>
                            </div>
                        </Popup>
                    </CircleMarker>
                ))}
            </MapContainer>
        </div>
    );
};

export default AttackMap;
