import React, { useState, useRef, useEffect, useCallback } from "react";
import { Wrapper, Status } from "@googlemaps/react-wrapper";

interface GoogleMapSelectorProps {
  onLocationSelect: (
    coordinates: { lat: number; lng: number },
    zoom?: number
  ) => void;
}

const MapComponent: React.FC<GoogleMapSelectorProps> = ({
  onLocationSelect,
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const searchBoxRef = useRef<HTMLInputElement>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const [marker, setMarker] =
    useState<google.maps.marker.AdvancedMarkerElement | null>(null);
  const [autocomplete, setAutocomplete] =
    useState<google.maps.places.Autocomplete | null>(null);
  const [selectedPlace, setSelectedPlace] = useState<{
    coordinates: { lat: number; lng: number };
    name: string;
  } | null>(null);
  const [hasProceeded, setHasProceeded] = useState(false);

  // Memoize the location select callback to prevent unnecessary re-renders
  const handleLocationSelect = useCallback(
    (coordinates: { lat: number; lng: number }, locationName?: string) => {
      // Log coordinates to console
      console.log("📍 Selected Coordinates:", coordinates);
      console.log(`Latitude: ${coordinates.lat}`);
      console.log(`Longitude: ${coordinates.lng}`);
      if (locationName) {
        console.log(`Location: ${locationName}`);
      }

      onLocationSelect(coordinates, map?.getZoom() || 13);
    },
    [onLocationSelect]
  );

  // Create a red pin marker using Advanced Marker
  const createRedMarker = async (
    position: google.maps.LatLng,
    title?: string,
    mapInstance?: google.maps.Map
  ) => {
    const targetMap = mapInstance || map;
    if (!targetMap) {
      console.error("Map not available for marker creation");
      return null;
    }

    try {
      // Import the marker library
      const markerLibrary = (await google.maps.importLibrary(
        "marker"
      )) as google.maps.MarkerLibrary;

      console.log(
        "Creating advanced marker at:",
        position.lat(),
        position.lng()
      );

      // Create a custom red pin
      const pinElement = new markerLibrary.PinElement({
        background: "#FF4444",
        borderColor: "#FFFFFF",
        glyphColor: "#FFFFFF",
        scale: 1.2,
      });

      return new markerLibrary.AdvancedMarkerElement({
        map: targetMap,
        position: position,
        title: title || "Selected Location",
        content: pinElement.element,
      });
    } catch (error) {
      console.error("Error creating advanced marker:", error);
      return null;
    }
  };

  // Handle proceeding with the selected location
  const handleProceedWithLocation = () => {
    if (selectedPlace) {
      handleLocationSelect(selectedPlace.coordinates, selectedPlace.name);
      setSelectedPlace(null);
      setHasProceeded(true);
    } else if (map) {
      // If no specific location is selected, use the current map center
      const center = map.getCenter();
      const zoom = map.getZoom();
      const coordinates = {
        lat: center?.lat() || 0,
        lng: center?.lng() || 0,
      };

      console.log("📍 Current Map Center:", coordinates);
      console.log(`Latitude: ${coordinates.lat}`);
      console.log(`Longitude: ${coordinates.lng}`);
      console.log(`Zoom Level: ${zoom}`);

      handleLocationSelect(coordinates, "Current Map Center");
      setHasProceeded(true);
    }
  };

  // Handle going back to map view
  const handleBackToMap = () => {
    setHasProceeded(false);
    setSelectedPlace(null);
    if (marker) {
      marker.map = null;
    }
  };

  useEffect(() => {
    if (mapRef.current && !map) {
      try {
        const newMap = new google.maps.Map(mapRef.current, {
          center: { lat: 43.65107, lng: -79.347015 }, // Default to Toronto
          zoom: 13,
          mapTypeId: google.maps.MapTypeId.HYBRID, // Use hybrid to show labels on satellite
          mapTypeControl: true,
          streetViewControl: false,
          fullscreenControl: true,
          zoomControl: true,
          gestureHandling: "cooperative",
          mapId: "DEMO_MAP_ID", // Required for advanced markers
          // Enable labels and features
          clickableIcons: true,
          disableDefaultUI: false,
        });

        console.log("Map initialized successfully");
        setMap(newMap); // Set map state immediately after creation

        // Initialize Autocomplete with proper configuration
        if (searchBoxRef.current) {
          console.log("Initializing Google Places Autocomplete...");
          const autocompleteInstance = new google.maps.places.Autocomplete(
            searchBoxRef.current,
            {
              types: ["geocode", "establishment"],
              componentRestrictions: { country: ["us", "ca"] }, // Restrict to US and Canada
              fields: ["place_id", "geometry", "name", "formatted_address"],
            }
          );
          setAutocomplete(autocompleteInstance);
          console.log("Autocomplete initialized successfully");

          // Listen for place selection
          autocompleteInstance.addListener("place_changed", async () => {
            const place = autocompleteInstance.getPlace();

            if (!place.geometry || !place.geometry.location) {
              console.log(
                "No details available for input: '" + place.name + "'"
              );
              return;
            }

            // Clear out the old marker
            if (marker) {
              marker.map = null;
            }

            // Create new red marker for searched location
            const newMarker = await createRedMarker(
              place.geometry.location,
              place.name || undefined,
              newMap
            );
            if (newMarker) {
              setMarker(newMarker);
              console.log("Advanced marker placed successfully");
            }

            // Store the selected place for the proceed button
            const coordinates = {
              lat: place.geometry.location.lat(),
              lng: place.geometry.location.lng(),
            };

            setSelectedPlace({
              coordinates: coordinates,
              name: place.name || "Selected Location",
            });

            // Log the searched location coordinates
            console.log("🔍 Searched Location:", place.name);
            console.log("📍 Searched Coordinates:", coordinates);
            console.log("Zoom:", newMap.getZoom());

            // If the place has a viewport, center the map on it
            if (place.geometry.viewport) {
              newMap.fitBounds(place.geometry.viewport);
            } else {
              newMap.setCenter(place.geometry.location);
              newMap.setZoom(16); // More zoomed in for better detail
            }
          });
        }

        // Add click listener to the map
        const clickListener = newMap.addListener(
          "click",
          async (event: google.maps.MapMouseEvent) => {
            const position = event.latLng;
            if (position) {
              // Remove existing marker
              if (marker) {
                marker.map = null;
              }

              // Create new red marker for clicked location
              const newMarker = await createRedMarker(
                position,
                "Clicked Location",
                newMap
              );
              if (newMarker) {
                setMarker(newMarker);
              }

              // Store the selected place for the proceed button
              const coordinates = {
                lat: position.lat(),
                lng: position.lng(),
              };

              setSelectedPlace({
                coordinates: coordinates,
                name: "Clicked Location",
              });

              // Call the callback with coordinates
              handleLocationSelect(coordinates);
            }
          }
        );

        // Cleanup function
        return () => {
          google.maps.event.removeListener(clickListener);
          if (marker) {
            marker.map = null;
          }
        };
      } catch (error) {
        console.error("Error initializing Google Maps:", error);
      }
    }
  }, [map, marker, handleLocationSelect]);

  // Cleanup marker when component unmounts
  useEffect(() => {
    return () => {
      if (marker) {
        marker.map = null;
      }
    };
  }, [marker]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const searchValue = e.target.value;

    if (!searchValue) {
      setSelectedPlace(null);
      return;
    }
  };

  return (
    <div className="w-full space-y-4">
      {!hasProceeded ? (
        <>
          {/* Search Box with Autocomplete */}
          <div className="relative">
            <input
              ref={searchBoxRef}
              type="text"
              onChange={handleSearchChange}
              placeholder="Search for a place or address..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
              autoComplete="off"
              style={{
                position: "relative",
                zIndex: 1000,
              }}
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              <svg
                className="h-5 w-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>

          {/* Map */}
          <div className="w-full h-96 rounded-lg overflow-hidden shadow-lg">
            <div ref={mapRef} className="w-full h-full" />
          </div>

          {/* Proceed Button */}
          <div
            className={`border rounded-lg p-4 ${
              selectedPlace
                ? "bg-green-50 border-green-200"
                : "bg-blue-50 border-blue-200"
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                {selectedPlace ? (
                  <>
                    <p className="text-sm font-medium text-green-800">
                      Location Selected: {selectedPlace.name}
                    </p>
                    <p className="text-xs text-green-600">
                      Lat: {selectedPlace.coordinates.lat.toFixed(6)}, Lng:{" "}
                      {selectedPlace.coordinates.lng.toFixed(6)}
                    </p>
                  </>
                ) : (
                  <>
                    <p className="text-sm font-medium text-blue-800">
                      No specific location selected
                    </p>
                    <p className="text-xs text-blue-600">
                      Click "Proceed with Location" to use the current map
                      center
                    </p>
                  </>
                )}
              </div>
              <button
                onClick={handleProceedWithLocation}
                className={`font-medium py-2 px-4 rounded-lg transition-colors duration-200 ${
                  selectedPlace
                    ? "bg-green-600 hover:bg-green-700 text-white"
                    : "bg-blue-600 hover:bg-blue-700 text-white"
                }`}
              >
                Proceed with Location
              </button>
            </div>
          </div>
        </>
      ) : (
        /* Back Button */
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <div className="text-center">
            <div className="text-green-600 text-2xl mb-2">✅</div>
            <p className="text-lg font-medium text-gray-800 mb-2">
              Location Analysis Started
            </p>
            <p className="text-sm text-gray-600 mb-4">
              Your selected location has been sent for analysis. You can return
              to the map to select a different location.
            </p>
            <button
              onClick={handleBackToMap}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors duration-200"
            >
              ← Back to Map
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const render = (status: Status) => {
  switch (status) {
    case Status.LOADING:
      return (
        <div className="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <span className="ml-2 text-gray-600">Loading Google Maps...</span>
        </div>
      );
    case Status.FAILURE:
      return (
        <div className="flex items-center justify-center h-96 bg-red-50 rounded-lg">
          <div className="text-center">
            <div className="text-red-600 text-2xl mb-2">⚠️</div>
            <p className="text-red-600">Failed to load Google Maps</p>
            <p className="text-sm text-gray-500 mt-1">
              Please check your API key and internet connection
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Make sure REACT_APP_GOOGLE_MAPS_API_KEY is set in your .env file
            </p>
          </div>
        </div>
      );
    default:
      return (
        <div className="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
          <span className="text-gray-600">Initializing map...</span>
        </div>
      );
  }
};

const GoogleMapSelector: React.FC<GoogleMapSelectorProps> = ({
  onLocationSelect,
}) => {
  const apiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

  if (!apiKey) {
    return (
      <div className="flex items-center justify-center h-96 bg-yellow-50 rounded-lg">
        <div className="text-center">
          <div className="text-yellow-600 text-2xl mb-2">🔑</div>
          <p className="text-yellow-600">Google Maps API Key Required</p>
          <p className="text-sm text-gray-500 mt-1">
            Please set REACT_APP_GOOGLE_MAPS_API_KEY in your .env file
          </p>
          <p className="text-xs text-gray-400 mt-2">
            See GOOGLE_MAPS_SETUP.md for instructions
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Current value: {apiKey || "undefined"}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Check browser console for debug info
          </p>
        </div>
      </div>
    );
  }

  return (
    <Wrapper apiKey={apiKey} libraries={["places", "marker"]} render={render}>
      <MapComponent onLocationSelect={onLocationSelect} />
    </Wrapper>
  );
};

export default GoogleMapSelector;
