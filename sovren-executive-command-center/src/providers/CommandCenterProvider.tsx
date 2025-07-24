'use client'

import React, { createContext, useContext, useState } from 'react'

interface CommandCenterContextType {
    sceneManager: any | null
    isInitialized: boolean
}

const CommandCenterContext = createContext<CommandCenterContextType | null>(null)

export const useCommandCenter = () => {
    const context = useContext(CommandCenterContext)
    if (!context) {
        throw new Error('useCommandCenter must be used within a CommandCenterProvider')
    }
    return context
}

interface CommandCenterProviderProps {
    children: React.ReactNode
}

export const CommandCenterProvider: React.FC<CommandCenterProviderProps> = ({ children }) => {
    const [sceneManager] = useState<any | null>(null)
    const [isInitialized] = useState(true)

    const value = {
        sceneManager,
        isInitialized
    }

    return (
        <CommandCenterContext.Provider value={value}>
            {children}
        </CommandCenterContext.Provider>
    )
}

export default CommandCenterProvider 